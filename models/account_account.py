from odoo import _, api, fields, models

class AccountAccount(models.Model):
  _inherit = 'account.account'

  prepayment = fields.Boolean(string="Prepayment")