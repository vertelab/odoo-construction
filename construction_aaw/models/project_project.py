# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    aaw_ids = fields.One2many(
        "construction.aaw",
        "project_id",
        string="ÄTA",
    )
    aaw_count = fields.Integer(
        string="ÄTA Count",
        compute="_compute_aaw_count",
    )
    aaw_amount_total = fields.Monetary(
        string="ÄTA Total Amount",
        compute="_compute_aaw_amount",
        currency_field="currency_id",
    )

    @api.depends("aaw_ids")
    def _compute_aaw_count(self):
        for project in self:
            project.aaw_count = len(project.aaw_ids)

    @api.depends("aaw_ids.offer_amount")
    def _compute_aaw_amount(self):
        for project in self:
            project.aaw_amount_total = sum(project.aaw_ids.mapped("offer_amount"))

    def _get_next_aaw_name(self):
        """Get the next ÄTA number for this project."""
        self.ensure_one()
        sequence = self.env["ir.sequence"].next_by_code("construction.aaw")
        return sequence or "ÄTA 001"
