from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # TODO: Fix This binary field
    prepayment_invoice_outstanding_credits_debits_widget = fields.Binary(
        groups="account.group_account_invoice,account.group_account_readonly",
        compute='_compute_payments_widget_to_reconcile_info',
        exportable=False,
    )
 

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
