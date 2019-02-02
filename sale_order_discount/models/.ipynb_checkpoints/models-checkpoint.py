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

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    discount_method = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], default='fixed')
    discount_amount = fields.Float(string='Discount amount', default="0.0")
    total_discount = fields.Monetary(string='Discount', compute="_amount_all")            
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=False, readonly=True, compute='_amount_all',
                                   track_visibility='always')

    @api.onchange('order_line.price_total', 'discount_amount')
    def _amount_all(self):
        """
        Compute the total discount of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = total_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if order.discount_method == 'fixed':
                total_discount = 0 - order.discount_amount
            else:
                total_discount = 0 - ((amount_untaxed + amount_tax) * order.discount_amount / 100) 
            order.update({
                'total_discount': order.pricelist_id.currency_id.round(total_discount),
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax + total_discount
            })
                
    @api.multi
    def _prepare_invoice(self,):
        invoice_vals = super(SaleOrderInherit, self)._prepare_invoice()
        invoice_vals.update({
            'discount_method': self.discount_method,
            'discount_amount': self.discount_amount
        })
        return invoice_vals

class AccountInvoiceDiscount(models.Model):
    _inherit = 'account.invoice'
    
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'discount_amount', 'discount_method')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        if self.discount_method == 'fixed':
            self.total_discount = 0 - self.discount_amount
        else:
            self.total_discount = 0 - ((self.amount_untaxed + self.amount_tax) * self.discount_amount / 100)
        self.amount_total = self.amount_untaxed + self.amount_tax + self.total_discount
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    discount_method = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], default='fixed')
    discount_amount = fields.Float(string='Discount amount', default="0.0")
    total_discount = fields.Monetary(string='Discount', compute="_compute_amount")            
    amount_untaxed = fields.Monetary(string='Untaxed Amount',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount in Company Currency', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax',
        store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Total',
        store=False, readonly=True, compute='_compute_amount')
    amount_total_signed = fields.Monetary(string='Total in Invoice Currency', currency_field='currency_id',
        store=False, readonly=True, compute='_compute_amount',
        help="Total amount in the currency of the invoice, negative for credit notes.")
    amount_total_company_signed = fields.Monetary(string='Total in Company Currency', currency_field='company_currency_id', store=True, readonly=True, compute='_compute_amount',
        help="Total amount in the currency of the company, negative for credit notes.")

