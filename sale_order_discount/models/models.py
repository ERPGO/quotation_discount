# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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

    @api.onchange('order_line.price_total')
    def _amount_all( self ):
        """
        Compute the total discount of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = total_discount = total = 0.0
            for line in order.order_line:
                total += round((line.product_uom_qty * line.price_unit))
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                total_discount = 0 - (total - amount_untaxed)
            order.update({
                'total_unit_price': order.pricelist_id.currency_id.round(total),
                'total_discount': order.pricelist_id.currency_id.round(total_discount),
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax
            })

    @api.onchange('discount_method', 'discount_amount', 'order_line')
    def supply_rate( self ):
        for order in self:
            if order.discount_method == 'percentage':
                if order.discount_amount > 100 or order.discount_amount < 0:
                    raise ValidationError(_('Enter Discount percentage between 0-100.'))
                for line in order.order_line:
                    line.discount = order.discount_amount
            else:
                total = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                if order.discount_amount != 0 and total > 0:
                    discount = (order.discount_amount / total) * 100
                else:
                    discount = order.discount_amount
                for line in order.order_line:
                    line.discount = discount

    @api.multi
    def _prepare_invoice( self, ):
        invoice_vals = super(SaleOrderInherit, self)._prepare_invoice()
        invoice_vals.update({
            'discount_method': self.discount_method,
            'discount_amount': self.discount_amount
        })
        return invoice_vals

    @api.multi
    def button_dummy( self ):
        self.supply_rate()
        return True

    total_unit_price = fields.Monetary(string='Sub Total', store=False, readonly=True, compute='_amount_all',
                                       track_visibility='always')
    discount_method = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], readonly=True,
                                       states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                       default='fixed')
    discount_amount = fields.Float(string='Discount amount', readonly=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                   default="0.0")
    total_discount = fields.Monetary(string='Discount', readonly=True, compute="_amount_all",
                                     track_visibility='always')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=False, readonly=True, compute='_amount_all',
                                   track_visibility='always')


class AccountInvoiceDiscount(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'discount_amount', 'discount_method')
    def _compute_amount( self ):
        round_curr = self.currency_id.round
        for inv in self:
            amount_untaxed = total_discount = total = 0.0
            for line in inv.invoice_line_ids:
                amount_untaxed += line.price_subtotal
                total += round((line.quantity * line.price_unit))
                total_discount = 0 - (total - amount_untaxed)
            inv.update({
                'total_unit_price': inv.currency_id.round(total),
                'total_discount': inv.currency_id.round(total_discount),
            })
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
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

    @api.onchange('discount_method', 'discount_amount', 'invoice_line_ids')
    def supply_rate( self ):
        for inv in self:
            if inv.discount_method == 'percentage':
                if inv.discount_amount > 100 or inv.discount_amount < 0:
                    raise ValidationError(_('Enter Discount percentage between 0-100.'))
                for line in inv.invoice_line_ids:
                    line.discount = inv.discount_amount
            else:
                total = 0.0
                for line in inv.invoice_line_ids:
                    total += round((line.quantity * line.price_unit))
                if inv.discount_amount != 0 and total > 0:
                    discount = (inv.discount_amount / total) * 100
                else:
                    discount = inv.discount_amount
                for line in inv.invoice_line_ids:
                    line.discount = discount

    @api.multi
    def button_dummy( self ):
        self.supply_rate()
        return True

    discount_method = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], readonly=True,
                                       states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                       default='fixed')
    discount_amount = fields.Float(string='Discount amount', readonly=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                   default="0.0")
    total_discount = fields.Monetary(string='Discount', store=False, compute="_compute_amount",
                                     track_visibility='always')
    total_unit_price = fields.Monetary(string='Sub Total', store=False, readonly=True, compute='_compute_amount',
                                       track_visibility='always')

    amount_untaxed = fields.Monetary(string='Untaxed Amount',
                                     store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount in Company Currency',
                                            currency_field='company_currency_id',
                                            store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax',
                                 store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Total',
                                   store=False, readonly=True, compute='_compute_amount')
    amount_total_signed = fields.Monetary(string='Total in Invoice Currency', currency_field='currency_id',
                                          store=False, readonly=True, compute='_compute_amount',
                                          help="Total amount in the currency of the invoice, negative for credit notes.")
    amount_total_company_signed = fields.Monetary(string='Total in Company Currency',
                                                  currency_field='company_currency_id', store=True, readonly=True,
                                                  compute='_compute_amount',
                                                  help="Total amount in the currency of the company, negative for credit notes.")
