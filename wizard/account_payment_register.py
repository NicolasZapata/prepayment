from odoo import _, api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.depends("available_journal_ids")
    def _compute_journal_id(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                batch = wizard._get_batches()[0]
                wizard.journal_id = wizard._get_batch_journal(batch)
            else:
                wizard.journal_id = self.env["account.journal"].search(
                    [
                        ("type", "in", ("bank", "cash", "crossed_prepayment")),
                        ("company_id", "=", wizard.company_id.id),
                        ("id", "in", self.available_journal_ids.ids),
                    ],
                    limit=1,
                )
