# -*- coding: utf-8 -*-
{
    'name': "Total Discount on SO",

    'summary': """
        Total discounts on quotations""",

    'description': """
        Total discounts on quotations
    """,

    'author': "ERPGO",
    'website': "http://www.erpgo.az",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'account_invoicing'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/sale_order.xml',
        'views/account_invoice.xml',
        'views/account_invoice_reporting.xml',
        'views/sale_order_reporting.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
