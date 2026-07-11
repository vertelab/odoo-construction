# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SignMixin(models.AbstractModel):
    _name = "sign.mixin"
    _description = "Mixin for models that support digital signing via sign_oca"

    sign_request_ids = fields.One2many(
        "sign.oca.request",
        "res_id",
        string="Sign Requests",
        domain=lambda self: [("res_model", "=", self._name)],
        copy=False,
    )
    sign_request_count = fields.Integer(
        string="Sign Request Count",
        compute="_compute_sign_request_count",
        compute_sudo=True,
    )
    is_signed = fields.Boolean(
        string="Signed",
        compute="_compute_is_signed",
        compute_sudo=True,
        store=True,
    )

    @api.depends("sign_request_ids")
    def _compute_sign_request_count(self):
        for record in self:
            record.sign_request_count = len(record.sign_request_ids)

    @api.depends("sign_request_ids.state")
    def _compute_is_signed(self):
        for record in self:
            if not record.sign_request_ids:
                record.is_signed = False
            else:
                record.is_signed = all(
                    req.state == "signed" for req in record.sign_request_ids
                )

    def action_view_sign_requests(self):
        """Open filtered sign request view for this record."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Sign Requests"),
            "res_model": "sign.oca.request",
            "view_mode": "tree,form",
            "domain": [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
            ],
            "context": {"create": False},
        }

    def action_request_signature(self):
        """Create a sign request and send notification to the partner."""
        self.ensure_one()
        if not hasattr(self, "partner_id") or not self.partner_id:
            raise models.ValidationError(
                _("A partner must be set on the record before requesting signature.")
            )

        sign_template = self._get_sign_template()
        if not sign_template:
            raise models.ValidationError(
                _("No sign template configured. Contact your administrator.")
            )

        sign_request = (
            self.env["sign.oca.request"]
            .sudo()
            .create(
                sign_template._prepare_sign_oca_request_vals_from_record(self)
            )
        )
        sign_request.action_send()

        self.message_post(
            body=_("Signature requested from %s.", self.partner_id.name),
        )

    def _get_sign_template(self):
        """Get the sign.oca.template to use. Override per model."""
        return self.env["sign.oca.template"].sudo().search([], limit=1)


class SignOcaRequest(models.Model):
    """Extend sign.oca.request with generic model reference fields."""

    _inherit = "sign.oca.request"

    res_model = fields.Char(
        string="Resource Model",
        index=True,
    )
    res_id = fields.Integer(
        string="Resource ID",
        index=True,
    )

    def _compute_resource_ref(self):
        """Compute the referenced record for display."""
        for req in self:
            req.resource_ref = False
            if req.res_model and req.res_id:
                req.resource_ref = (
                    self.env[req.res_model].sudo().browse(req.res_id)
                )

    resource_ref = fields.Reference(
        string="Resource",
        compute="_compute_resource_ref",
        selection="_selection_resource_ref",
    )

    @api.model
    def _selection_resource_ref(self):
        """Return models that can be signed."""
        return [
            ("construction.aaw", "ÄTA"),
            ("project.task", "Task"),
            ("project.project", "Project"),
        ]
