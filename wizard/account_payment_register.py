from odoo import _, api, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"
