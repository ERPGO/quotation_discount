# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class sale_order_discount(models.Model):
#     _name = 'sale_order_discount.sale_order_discount'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class sale_order_discount(models.Model):
    _inherit = 'sale.order'
    
    discount_method = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')])
    discount_amount = fields.Float(string='Discount amount', default="0.0")
    total_discount = fields.Monetary(string='Discount', compute="_get_discount")
    
    @api.depends('discount_method')
    def _get_discount(self):
        total_discount = 0.0
        if self.discount_method == 'fixed':
            total_discount = self.discount_amount
        elif self.discount_method == 'percentage':
            total_discount = self.amount_total * self.discount_amount / 100
        return total_discount
        
    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total discount of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'total_discount': self._get_discount(),
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax - self._get_discount(),
            })

    