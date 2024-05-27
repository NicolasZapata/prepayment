from odoo import _, api, fields, models
from odoo.tools import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    prepayment_invoice_outstanding_credits_debits_widget = fields.Binary(
        compute="_compute_prepayments_widget",
        exportable=False,
    )

    invoice_prepayments_widget = fields.Binary(
        groups="account.group_account_invoice,account.group_account_readonly",
        compute="_compute_prepayments_widget_account",
        exportable=False,
    )

    @api.depends("move_type", "line_ids.amount_residual")
    def _compute_prepayments_widget_account(self):
        for move in self:
            payments_widget_vals = {
                "title": _("Less Prepaayment"),
                "outstanding": False,
                "content": [],
            }
            if move.state == "posted" and move.is_invoice(include_receipts=True):
                reconciled_vals = []
                reconciled_partials = move._get_all_reconciled_invoice_partials()
                for reconciled_partial in reconciled_partials:
                    counterpart_line = reconciled_partial["aml"]
                    if counterpart_line.move_id.ref:
                        reconciliation_ref = "%s (%s)" % (
                            counterpart_line.move_id.name,
                            counterpart_line.move_id.ref,
                        )
                    else:
                        reconciliation_ref = counterpart_line.move_id.name
                    if (
                        counterpart_line.amount_currency
                        and counterpart_line.currency_id
                        != counterpart_line.company_id.currency_id
                    ):
                        foreign_currency = counterpart_line.currency_id
                    else:
                        foreign_currency = False
                    reconciled_vals.append(
                        {
                            "name": counterpart_line.name,
                            "journal_name": counterpart_line.journal_id.name,
                            "amount": reconciled_partial["amount"],
                            "currency_id": (
                                move.company_id.currency_id.id
                                if reconciled_partial["is_exchange"]
                                else reconciled_partial["currency"].id
                            ),
                            "date": counterpart_line.date,
                            "partial_id": reconciled_partial["partial_id"],
                            "account_payment_id": counterpart_line.payment_id.id,
                            "payment_method_name": counterpart_line.payment_id.payment_method_line_id.name,
                            "move_id": counterpart_line.move_id.id,
                            "ref": reconciliation_ref,
                            # these are necessary for the views to change depending on the values
                            "is_exchange": reconciled_partial["is_exchange"],
                            "amount_company_currency": formatLang(
                                self.env,
                                abs(counterpart_line.balance),
                                currency_obj=counterpart_line.company_id.currency_id,
                            ),
                            "amount_foreign_currency": foreign_currency
                            and formatLang(
                                self.env,
                                abs(counterpart_line.amount_currency),
                                currency_obj=foreign_currency,
                            ),
                        }
                    )
                payments_widget_vals["content"] = reconciled_vals
            if payments_widget_vals["content"]:
                move.invoice_prepayments_widget = payments_widget_vals
            else:
                move.invoice_prepayments_widget = False

    def _compute_prepayments_widget(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = False
            move.invoice_has_outstanding = False
            # if (
            #     move.state != "posted"
            #     or move.payment_state not in ("not_paid", "partial")
            #     or not move.is_invoice(include_receipts=True)
            # ):
            #     continue
            pay_term_lines = move.line_ids.filtered(
                lambda line: line.account_id.account_type
                in ("asset_receivable", "liability_payable")
            )
            domain = [
                # ("account_id", "in", pay_term_lines.account_id.ids),
                # ("parent_state", "=", "posted"),
                # ("partner_id", "=", move.commercial_partner_id.id),
                # ("reconciled", "=", False),
                # "|",
                # ("amount_residual", "!=", 0.0),
                # ("amount_residual_currency", "!=", 0.0),
                ("account_id.prepayment", "!=", False),
            ]
            payments_widget_vals = {
                "outstanding": True,
                "content": [],
                "move_id": move.id,
            }
            if move.is_inbound():
                # domain.append(("balance", "<", 0.0))
                payments_widget_vals["title"] = _("Prepayment Credits")
            # else:
            #     domain.append(("balance", ">", 0.0))
            #     payments_widget_vals["title"] = _("Outstanding debits")
            for line in self.env["account.move.line"].search(domain):
                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.
                    amount = line.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )
                if move.currency_id.is_zero(amount):
                    continue
                payments_widget_vals["content"].append(
                    {
                        "journal_name": line.ref or line.move_id.name,
                        "amount": amount,
                        "currency_id": move.currency_id.id,
                        "id": line.id,
                        "move_id": line.move_id.id,
                        "date": fields.Date.to_string(line.date),
                        "account_payment_id": line.payment_id.id,
                    }
                )
            # if not payments_widget_vals["content"]:
            #     continue
            move.prepayment_invoice_outstanding_credits_debits_widget = (
                payments_widget_vals
            )
            move.invoice_has_outstanding = True

    def action_register_prepayment(self):
        """Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        """
        prepayment_journal_id = self.env["account.journal"].search(
            [
                ("type", "in", ("bank", "cash", "crossed_prepayment")),
                ("company_id", "=", self.company_id.id),
            ],
            limit=1,
        )
        return {
            "name": _("Register Payment"),
            "res_model": "account.payment.register",
            "view_mode": "form",
            "context": {
                "active_model": "account.move",
                "active_ids": self.ids,
                "journal_id": prepayment_journal_id,
            },
            "target": "new",
            "type": "ir.actions.act_window",
        }
