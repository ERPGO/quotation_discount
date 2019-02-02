# -*- coding: utf-8 -*-
from odoo import http

# class SaleOrderDiscount(http.Controller):
#     @http.route('/sale_order_discount/sale_order_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_discount/sale_order_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_discount.listing', {
#             'root': '/sale_order_discount/sale_order_discount',
#             'objects': http.request.env['sale_order_discount.sale_order_discount'].search([]),
#         })

#     @http.route('/sale_order_discount/sale_order_discount/objects/<model("sale_order_discount.sale_order_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_discount.object', {
#             'object': obj
#         })