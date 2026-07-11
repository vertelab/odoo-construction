# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ConstructionAawSurchargeTemplate(models.Model):
    _name = "construction.aaw.surcharge.template"
    _description = "ÄTA Surcharge Template"
    _order = "name"

    name = fields.Char(
        string="Template Name",
        required=True,
    )
    surcharge_percent = fields.Float(
        string="Surcharge %",
        required=True,
        default=0.0,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
