# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ConstructionAaw(models.Model):
    _name = "construction.aaw"
    _description = "ÄTA (Change Order)"
    _inherit = ["mail.thread", "mail.activity.mixin", "sign.mixin"]
    _order = "project_id, name"
    _rec_name = "name"

    # -- Identification ------------------------------------------------------
    name = fields.Char(
        string="ÄTA Number",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True,
    )
    contract_id = fields.Many2one(
        "contract.contract",
        string="Contract",
        ondelete="restrict",
        index=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        related="project_id.partner_id",
        store=True,
        readonly=False,
    )
    partner_contact_id = fields.Many2one(
        "res.partner",
        string="Customer Contact",
        domain="[('parent_id', '=', partner_id)]",
    )
    description = fields.Html(
        string="Description",
        translate=True,
    )
    aaw_type = fields.Selection(
        selection=[
            ("andring", "Ändring"),
            ("tillagg", "Tillägg"),
            ("avgaende", "Avgående"),
        ],
        string="ÄTA Type",
        default="andring",
        required=True,
    )

    # -- Financial -----------------------------------------------------------
    compensation_method = fields.Selection(
        selection=[
            ("fixed_price", "Fast pris"),
            ("unit_price", "À-pris"),
            ("cost_plus", "Löpande räkning"),
        ],
        string="Compensation Method",
        default="cost_plus",
        required=True,
    )
    estimated_amount = fields.Monetary(
        string="Estimated Amount",
        currency_field="currency_id",
    )
    surcharge_template_id = fields.Many2one(
        "construction.aaw.surcharge.template",
        string="Surcharge Template",
    )
    surcharge_amount = fields.Monetary(
        string="Surcharge Amount",
        compute="_compute_financials",
        store=True,
        currency_field="currency_id",
    )
    offer_amount = fields.Monetary(
        string="Offer Amount",
        compute="_compute_financials",
        store=True,
        currency_field="currency_id",
    )
    agreed_amount = fields.Monetary(
        string="Agreed Amount",
        currency_field="currency_id",
    )
    cost_total = fields.Monetary(
        string="Total Cost",
        compute="_compute_cost_revenue",
        store=True,
        currency_field="currency_id",
    )
    revenue_total = fields.Monetary(
        string="Total Revenue",
        compute="_compute_cost_revenue",
        store=True,
        currency_field="currency_id",
    )
    uninvoiced_amount = fields.Monetary(
        string="Uninvoiced Amount",
        compute="_compute_cost_revenue",
        store=True,
        currency_field="currency_id",
    )
    hide_surcharge = fields.Boolean(
        string="Hide Surcharge",
        default=False,
        help="Hide surcharge in reports and invoices.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="project_id.currency_id",
        store=True,
    )

    # -- State & ABT06 -------------------------------------------------------
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("invoiced", "Invoiced"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    notification_date = fields.Date(
        string="Notification Date (§9)",
        readonly=True,
    )
    written_order_date = fields.Date(
        string="Written Order Date (§8)",
        readonly=True,
    )
    approved_date = fields.Date(
        string="Approved Date",
        readonly=True,
    )
    completed_date = fields.Date(
        string="Completed Date",
        readonly=True,
    )
    invoice_date = fields.Date(
        string="Last Invoice Date",
        readonly=True,
    )
    closed_date = fields.Date(
        string="Closed Date",
        readonly=True,
    )
    time_extension_days = fields.Integer(
        string="Time Extension (days)",
        default=0,
    )
    time_extension_approved = fields.Boolean(
        string="Time Extension Approved",
        default=False,
    )
    customer_approved = fields.Boolean(
        string="Customer Approved (Portal)",
        default=False,
    )
    customer_comment = fields.Text(
        string="Customer Comment",
    )
    is_invoiced = fields.Boolean(
        string="Fully Invoiced",
        compute="_compute_is_invoiced",
        store=True,
    )

    # -- Relations -----------------------------------------------------------
    order_line_ids = fields.One2many(
        "construction.aaw.line",
        "aaw_id",
        string="Order Lines",
        copy=True,
    )
    invoice_ids = fields.Many2many(
        "account.move",
        string="Invoices",
        copy=False,
    )
    task_ids = fields.One2many(
        "project.task",
        "aaw_id",
        string="Tasks",
        copy=False,
    )

    # -- Other ---------------------------------------------------------------
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        tracking=True,
    )
    internal_notes = fields.Html(
        string="Internal Notes",
    )

    # -- Computed fields -----------------------------------------------------

    @api.depends("order_line_ids.estimated_quantity", "order_line_ids.unit_price",
                 "order_line_ids.surcharge_percent", "surcharge_template_id",
                 "surcharge_template_id.surcharge_percent")
    def _compute_financials(self):
        for aaw in self:
            estimated = 0.0
            surcharge = 0.0
            template_pct = aaw.surcharge_template_id.surcharge_percent if aaw.surcharge_template_id else None
            for line in aaw.order_line_ids:
                line_est = line.estimated_quantity * line.unit_price
                pct = template_pct if template_pct is not None else line.surcharge_percent
                line_surcharge = line_est * pct / 100.0
                estimated += line_est
                surcharge += line_surcharge
            aaw.estimated_amount = estimated
            aaw.surcharge_amount = surcharge
            aaw.offer_amount = estimated + surcharge

    @api.depends("order_line_ids.executed_quantity", "order_line_ids.cost_per_unit",
                 "order_line_ids.unit_price", "order_line_ids.surcharge_percent",
                 "order_line_ids.billable", "order_line_ids.sold_quantity",
                 "surcharge_template_id", "surcharge_template_id.surcharge_percent")
    def _compute_cost_revenue(self):
        for aaw in self:
            cost = 0.0
            revenue = 0.0
            uninvoiced = 0.0
            template_pct = aaw.surcharge_template_id.surcharge_percent if aaw.surcharge_template_id else None
            for line in aaw.order_line_ids:
                cost += line.executed_quantity * line.cost_per_unit
                if line.billable:
                    pct = template_pct if template_pct is not None else line.surcharge_percent
                    line_revenue = line.executed_quantity * line.unit_price
                    line_surcharge = line_revenue * pct / 100.0
                    revenue += line_revenue + line_surcharge
                    # Uninvoiced = (executed - sold) * (unit_price + surcharge)
                    unsold = line.executed_quantity - line.sold_quantity
                    if unsold > 0:
                        uninvoiced += unsold * line.unit_price
                        uninvoiced += unsold * line.unit_price * pct / 100.0
            aaw.cost_total = cost
            aaw.revenue_total = revenue
            aaw.uninvoiced_amount = uninvoiced

    @api.depends("uninvoiced_amount", "state")
    def _compute_is_invoiced(self):
        for aaw in self:
            aaw.is_invoiced = aaw.state == "done" and aaw.uninvoiced_amount <= 0

    # -- CRUD ----------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                project_id = vals.get("project_id")
                if project_id:
                    project = self.env["project.project"].browse(project_id)
                    vals["name"] = project._get_next_aaw_name()
                else:
                    vals["name"] = self.env["ir.sequence"].next_by_code("construction.aaw") or _("New")
        return super().create(vals_list)

    # -- State transitions ---------------------------------------------------

    def action_submit(self):
        """Submit ÄTA to customer for approval (§9 notification)."""
        for aaw in self:
            if not aaw.description:
                raise models.ValidationError(_("Description is required before submitting."))
            aaw.write({
                "state": "submitted",
                "notification_date": fields.Date.today(),
            })

    def action_approve(self):
        """Customer approves the ÄTA (§8 written order)."""
        for aaw in self:
            aaw.write({
                "state": "approved",
                "approved_date": fields.Date.today(),
                "written_order_date": fields.Date.today(),
            })

    def action_reject(self):
        """Customer rejects the ÄTA."""
        for aaw in self:
            if not aaw.customer_comment:
                raise models.ValidationError(_("Customer comment is required when rejecting."))
            aaw.write({"state": "rejected"})

    def action_start_work(self):
        """Start executing the approved ÄTA."""
        for aaw in self:
            aaw.write({"state": "in_progress"})

    def action_mark_done(self):
        """Mark ÄTA work as completed."""
        for aaw in self:
            aaw.write({
                "state": "done",
                "completed_date": fields.Date.today(),
            })

    def action_invoice(self):
        """Create invoice for billable lines."""
        self.ensure_one()
        # TODO: Implement invoice creation logic in a future task
        return {
            "type": "ir.actions.act_window",
            "name": _("Create Invoice"),
            "res_model": "account.move",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_move_type": "out_invoice",
                "default_partner_id": self.partner_id.id,
                "default_aaw_id": self.id,
            },
        }

    def action_close(self):
        """Close the ÄTA (final settlement)."""
        for aaw in self:
            aaw.write({
                "state": "closed",
                "closed_date": fields.Date.today(),
            })

    def action_cancel(self):
        """Cancel the ÄTA from draft or submitted states."""
        for aaw in self:
            if aaw.state not in ("draft", "submitted"):
                raise models.ValidationError(_("Only draft or submitted ÄTA can be cancelled."))
            aaw.write({"state": "cancelled"})

    def action_draft(self):
        """Reset to draft from submitted."""
        for aaw in self:
            if aaw.state != "submitted":
                raise models.ValidationError(_("Only submitted ÄTA can be reset to draft."))
            aaw.write({"state": "draft"})

    def _check_auto_invoiced(self):
        """Auto-transition to invoiced when all billable lines are invoiced."""
        for aaw in self.search([("state", "=", "done")]):
            if aaw.uninvoiced_amount <= 0:
                aaw.write({
                    "state": "invoiced",
                    "invoice_date": fields.Date.today(),
                })
