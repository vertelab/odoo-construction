# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ConstructionAawLine(models.Model):
    _name = "construction.aaw.line"
    _description = "ÄTA Order Line"
    _order = "sequence, id"

    aaw_id = fields.Many2one(
        "construction.aaw",
        string="ÄTA",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )
    name = fields.Char(
        string="Description",
        required=True,
    )
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        domain="[('deprecated', '=', False)]",
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
    )
    estimated_quantity = fields.Float(
        string="Estimated Quantity",
        default=1.0,
    )
    executed_quantity = fields.Float(
        string="Executed Quantity",
        default=0.0,
    )
    sold_quantity = fields.Float(
        string="Invoiced Quantity",
        default=0.0,
    )
    unit_price = fields.Monetary(
        string="Unit Price",
        currency_field="currency_id",
        default=0.0,
    )
    cost_per_unit = fields.Monetary(
        string="Cost per Unit",
        currency_field="currency_id",
        default=0.0,
    )
    surcharge_percent = fields.Float(
        string="Surcharge %",
        default=0.0,
    )
    surcharge_amount = fields.Monetary(
        string="Surcharge Amount",
        compute="_compute_amounts",
        store=True,
        currency_field="currency_id",
    )
    offer_amount = fields.Monetary(
        string="Offer Amount",
        compute="_compute_amounts",
        store=True,
        currency_field="currency_id",
    )
    cost_subtotal = fields.Monetary(
        string="Cost Subtotal",
        compute="_compute_amounts",
        store=True,
        currency_field="currency_id",
    )
    billable = fields.Boolean(
        string="Billable",
        default=True,
    )
    executed_date = fields.Date(
        string="Executed Date",
    )
    comment = fields.Text(
        string="Comment",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="aaw_id.currency_id",
        store=True,
    )

    @api.depends("estimated_quantity", "executed_quantity", "unit_price",
                 "cost_per_unit", "surcharge_percent",
                 "aaw_id.surcharge_template_id",
                 "aaw_id.surcharge_template_id.surcharge_percent")
    def _compute_amounts(self):
        for line in self:
            template_pct = None
            if line.aaw_id.surcharge_template_id:
                template_pct = line.aaw_id.surcharge_template_id.surcharge_percent
            pct = template_pct if template_pct is not None else line.surcharge_percent

            line_est = line.estimated_quantity * line.unit_price
            line.surcharge_amount = line_est * pct / 100.0
            line.offer_amount = line_est + line.surcharge_amount
            line.cost_subtotal = line.executed_quantity * line.cost_per_unit
