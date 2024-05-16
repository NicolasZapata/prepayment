from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_register_prepayment(self):
        """Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        """

        prepayment_journal_id = self.env["account.journal"].search(
            [
                ("type", "in", ("bank", "cash", "crossed_prepayment")),
                ("company_id", "=", self.company_id.id),
                # ("id", "in", self.available_journal_ids.ids),
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
