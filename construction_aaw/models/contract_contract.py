# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ContractContract(models.Model):
    _inherit = "contract.contract"

    aaw_ids = fields.One2many(
        "construction.aaw",
        "contract_id",
        string="ÄTA",
    )
    aaw_count = fields.Integer(
        string="ÄTA Count",
        compute="_compute_aaw_count",
    )

    @api.depends("aaw_ids")
    def _compute_aaw_count(self):
        for contract in self:
            contract.aaw_count = len(contract.aaw_ids)
