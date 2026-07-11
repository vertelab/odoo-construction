# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestConstructionAaw(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.Aaw = cls.env["construction.aaw"]
        cls.AawLine = cls.env["construction.aaw.line"]
        cls.SurchargeTemplate = cls.env["construction.aaw.surcharge.template"]
        cls.Partner = cls.env["res.partner"]
        cls.Currency = cls.env.ref("base.SEK")

        cls.partner = cls.Partner.create({"name": "Test Bygg AB"})
        cls.project = cls.Project.create({
            "name": "Test Projekt",
            "partner_id": cls.partner.id,
        })

    def _create_aaw(self, **kwargs):
        vals = {
            "project_id": self.project.id,
            "partner_id": self.partner.id,
            "description": "<p>Test ÄTA</p>",
            "aaw_type": "andring",
            "compensation_method": "cost_plus",
            **kwargs,
        }
        return self.Aaw.create(vals)

    # -- State Machine Tests -------------------------------------------------

    def test_01_create_aaw_is_draft(self):
        """New ÄTA should be created in draft state."""
        aaw = self._create_aaw()
        self.assertEqual(aaw.state, "draft")

    def test_02_submit_requires_description(self):
        """Submitting without description should fail."""
        aaw = self._create_aaw(description=False)
        with self.assertRaises(ValidationError):
            aaw.action_submit()

    def test_03_submit_sets_dates(self):
        """Submit should set notification_date and transition to submitted."""
        aaw = self._create_aaw()
        aaw.action_submit()
        self.assertEqual(aaw.state, "submitted")
        self.assertTrue(aaw.notification_date)

    def test_04_approve_sets_dates(self):
        """Approve should set approved_date, written_order_date, transition to approved."""
        aaw = self._create_aaw()
        aaw.action_submit()
        aaw.action_approve()
        self.assertEqual(aaw.state, "approved")
        self.assertTrue(aaw.approved_date)
        self.assertTrue(aaw.written_order_date)

    def test_05_reject_requires_comment(self):
        """Reject should require customer_comment."""
        aaw = self._create_aaw()
        aaw.action_submit()
        with self.assertRaises(ValidationError):
            aaw.action_reject()
        aaw.customer_comment = "Too expensive"
        aaw.action_reject()
        self.assertEqual(aaw.state, "rejected")

    def test_06_full_lifecycle(self):
        """Test full lifecycle: draft → submitted → approved → in_progress → done → closed."""
        aaw = self._create_aaw()
        aaw.action_submit()
        aaw.action_approve()
        aaw.action_start_work()
        self.assertEqual(aaw.state, "in_progress")
        aaw.action_mark_done()
        self.assertEqual(aaw.state, "done")
        self.assertTrue(aaw.completed_date)
        aaw.write({"state": "invoiced", "invoice_date": "2026-07-11"})
        self.assertEqual(aaw.state, "invoiced")
        aaw.action_close()
        self.assertEqual(aaw.state, "closed")
        self.assertTrue(aaw.closed_date)

    def test_07_cancel_from_draft(self):
        """Cancel should work from draft."""
        aaw = self._create_aaw()
        aaw.action_cancel()
        self.assertEqual(aaw.state, "cancelled")

    def test_08_cancel_from_submitted(self):
        """Cancel should work from submitted."""
        aaw = self._create_aaw()
        aaw.action_submit()
        aaw.action_cancel()
        self.assertEqual(aaw.state, "cancelled")

    def test_09_cannot_cancel_approved(self):
        """Cancel should fail from approved state."""
        aaw = self._create_aaw()
        aaw.action_submit()
        aaw.action_approve()
        with self.assertRaises(ValidationError):
            aaw.action_cancel()

    def test_10_reset_to_draft(self):
        """Reset to draft from submitted."""
        aaw = self._create_aaw()
        aaw.action_submit()
        aaw.action_draft()
        self.assertEqual(aaw.state, "draft")

    # -- Computed Fields Tests -----------------------------------------------

    def test_11_compute_financials(self):
        """Test computed financial fields from order lines."""
        aaw = self._create_aaw()
        self.env["construction.aaw.line"].create({
            "aaw_id": aaw.id,
            "name": "Line 1",
            "estimated_quantity": 10.0,
            "unit_price": 1000.0,
            "surcharge_percent": 15.0,
        })
        self.assertEqual(aaw.estimated_amount, 10000.0)
        self.assertEqual(aaw.surcharge_amount, 1500.0)
        self.assertEqual(aaw.offer_amount, 11500.0)

    def test_12_compute_cost_revenue(self):
        """Test cost and revenue computation."""
        aaw = self._create_aaw()
        self.env["construction.aaw.line"].create({
            "aaw_id": aaw.id,
            "name": "Line 1",
            "estimated_quantity": 10.0,
            "executed_quantity": 5.0,
            "unit_price": 1000.0,
            "cost_per_unit": 600.0,
            "billable": True,
        })
        self.assertEqual(aaw.cost_total, 3000.0)  # 5 * 600
        self.assertEqual(aaw.revenue_total, 5000.0)  # 5 * 1000

    def test_13_uninvoiced_amount(self):
        """Test uninvoiced amount calculation."""
        aaw = self._create_aaw()
        self.env["construction.aaw.line"].create({
            "aaw_id": aaw.id,
            "name": "Line 1",
            "estimated_quantity": 10.0,
            "executed_quantity": 10.0,
            "sold_quantity": 4.0,
            "unit_price": 1000.0,
            "cost_per_unit": 600.0,
            "billable": True,
        })
        # 6 unsold * 1000 = 6000
        self.assertTrue(aaw.uninvoiced_amount > 0)
        self.assertAlmostEqual(aaw.uninvoiced_amount, 6000.0, places=2)

    def test_14_is_invoiced(self):
        """Test is_invoiced when done and nothing uninvoiced."""
        aaw = self._create_aaw()
        self.env["construction.aaw.line"].create({
            "aaw_id": aaw.id,
            "name": "Line 1",
            "estimated_quantity": 5.0,
            "executed_quantity": 5.0,
            "sold_quantity": 5.0,
            "unit_price": 1000.0,
            "cost_per_unit": 600.0,
            "billable": True,
        })
        aaw.action_submit()
        aaw.action_approve()
        aaw.action_start_work()
        aaw.action_mark_done()
        self.assertTrue(aaw.is_invoiced)

    # -- Surcharge Template Tests --------------------------------------------

    def test_15_surcharge_template_overrides_lines(self):
        """Surcharge template should override per-line surcharge."""
        template = self.SurchargeTemplate.create({
            "name": "Standard 15%",
            "surcharge_percent": 15.0,
        })
        aaw = self._create_aaw(surcharge_template_id=template.id)
        self.env["construction.aaw.line"].create({
            "aaw_id": aaw.id,
            "name": "Line 1",
            "estimated_quantity": 10.0,
            "unit_price": 1000.0,
            "surcharge_percent": 5.0,  # individual 5%
        })
        # Template 15% should override
        self.assertAlmostEqual(aaw.surcharge_amount, 1500.0, places=2)

    def test_16_surcharge_template_removal_reverts(self):
        """Removing template should revert to individual line surcharges."""
        template = self.SurchargeTemplate.create({
            "name": "Standard 15%",
            "surcharge_percent": 15.0,
        })
        aaw = self._create_aaw(surcharge_template_id=template.id)
        self.env["construction.aaw.line"].create({
            "aaw_id": aaw.id,
            "name": "Line 1",
            "estimated_quantity": 10.0,
            "unit_price": 1000.0,
            "surcharge_percent": 5.0,
        })
        self.assertAlmostEqual(aaw.surcharge_amount, 1500.0, places=2)
        aaw.surcharge_template_id = False
        self.assertAlmostEqual(aaw.surcharge_amount, 500.0, places=2)

    # -- Sequence Tests ------------------------------------------------------

    def test_17_per_project_sequence(self):
        """Each project should have independent ÄTA numbering."""
        aaw1 = self._create_aaw()
        self.assertIn("ÄTA", aaw1.name)

        # Create another project
        project2 = self.Project.create({
            "name": "Test Projekt 2",
            "partner_id": self.partner.id,
        })
        aaw2 = self._create_aaw(project_id=project2.id)
        self.assertIn("ÄTA", aaw2.name)
        # Both get sequence numbers from the same global sequence
