from odoo import _, api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection([("crossed_prepayment", "Crossed Prepayment")])
