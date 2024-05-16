{
  'name': 'Prepayment Odoo by Grupo Quanam Colombia',
  'version': '1.0',
  'description': 'Payment System',
  'summary': 'Account Pre-Payment',
  'author': 'Grupo Quanam Colombia SAS',
  'website': 'https//grupoquanam.com.co',
  'license': 'LGPL-3',
  'category': 'account, payment, prepayment',
  'depends': [
    'account',
  ],
  'data': [
    'security/ir.model.access.csv',
    'views/account_account_view.xml',
    'views/account_move_view.xml',
    'views/account_journal_view.xml',
    'views/res_partner_view.xml',
    'wizard/account_payment_register_view.xml',
  ],
  'auto_install': False,
  'application': False,
  'assets': {
    
  }
}