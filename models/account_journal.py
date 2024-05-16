from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection(
        selection_add=[("crossed_prepayment", "Crossed Prepayment")],
        ondelete={
            "crossed_prepayment": "cascade",
        },
    )

    @api.depends('type', 'currency_id')
    def _compute_inbound_payment_method_line_ids(self):
        """
        Compute the inbound payment method line IDs based on the journal type and currency.
        """
        for journal in self:
            pay_method_line_ids_commands = [Command.clear()]
            if journal.type in ('bank', 'cash', 'crossed_prepayment'):
                default_methods = journal._default_inbound_payment_methods()
                pay_method_line_ids_commands += [Command.create({
                    'name': pay_method.name,
                    'payment_method_id': pay_method.id,
                }) for pay_method in default_methods]
            journal.inbound_payment_method_line_ids = pay_method_line_ids_commands


    @api.depends('type', 'currency_id')
    def _compute_outbound_payment_method_line_ids(self):
        """
        Compute the outbound payment method line IDs based on the journal type and currency.
        """
        for journal in self:
            pay_method_line_ids_commands = [Command.clear()]
            if journal.type in ('bank', 'cash', 'crossed_prepayment'):
                default_methods = journal._default_outbound_payment_methods()
                pay_method_line_ids_commands += [Command.create({
                    'name': pay_method.name,
                    'payment_method_id': pay_method.id,
                }) for pay_method in default_methods]
            journal.outbound_payment_method_line_ids = pay_method_line_ids_commands
