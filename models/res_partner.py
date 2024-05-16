from odoo import _, api, fields, models

class ResPartner(models.Model):
	_inherit = "res.partner"
	
	prepayment_account_id = fields.Many2one('account.account', string="Prepayment Account")