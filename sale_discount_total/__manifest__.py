# -*- coding: utf-8 -*-
{
    'name': 'Sale Discount on Total Amount',
    'version': '11.0.1.0.1',
    'category': 'Sales Management',
    'summary': "Discount on Total in Sale and Invoice With Discount Limit and Approval",
    'author': 'ERPGO.AZ',
    'company': 'ERPGO.AZ',
    'website': 'http://www.erpgo.az',
    'description': """

Sale Discount for Total Amount
=======================
Module to manage discount on total amount in Sale.
        as an specific amount or percentage
""",
    'depends': ['sale',
                'account'
                ],
    'data': [
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
        'views/invoice_report.xml',
        'views/sale_order_report.xml',
        'views/res_config_view.xml',

    ],
    'demo': [
    ],
    #'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
