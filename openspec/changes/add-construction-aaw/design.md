## Context

The current `contract_aaw` module models ÄTA (change orders) as a boolean flag `is_aaw` on `project.task`. This worked as a quick proof-of-concept but is fundamentally wrong for medium-to-large Swedish construction companies operating under AB04/ABT06:

- ÄTA has a **legally regulated lifecycle** (§§ 3–9) that doesn't map to task stages
- ÄTA needs **order lines** with quantity/cost/surcharge breakdown — task has none
- ÄTA requires **per-project numbering** and dedicated reporting
- ÄTA must connect to **contract budget** and **surcharge templates**
- Tasks have 100+ irrelevant fields, polluted in shared tables

Next Project's ÄTA module handles all of this natively. This design creates an equivalent in Odoo 18.

## Goals / Non-Goals

**Goals:**
- Standalone `construction.aaw` model with full ABT06 lifecycle
- Per-project ÄTA numbering (ÄTA 001, ÄTA 002, ...)
- Order lines with quantity, cost, surcharge, billable flag
- Surcharge templates that can override per-line surcharges
- Digital signing via generalized `sign.mixin`
- Relations to `project.project` and `contract.contract`

**Non-Goals:**
- SVA/prognos integration (Phase 2)
- Kalkylimport (Phase 2)
- Replacing `contract_aaw` internals (we deprecate, not migrate)
- Projektdagbok, KMA, BEAst, ID06

## Decisions

### Decision 1: Standalone model over project.task inheritance

**Chosen**: `construction.aaw` as `models.Model` (no inheritance from `project.task`)

**Alternatives considered**:
- A: Extend `project.task` with state field + workflow — rejected because task model bloats ÄTA with irrelevant fields, mixes ÄTA and regular tasks in same table, makes reporting and security harder
- B: Delegation inheritance (`_inherits`) — rejected because all task fields still appear in views, confusing users

**Rationale**: ÄTA is a first-class business object. Medium/large contractors expect dedicated ÄTA views, reports, and workflows. Clean separation enables dedicated ACLs and future extensions without breaking tasks.

### Decision 2: Module organization

```
odoo-construction/
├── construction_aaw/          # Core ÄTA module
│   ├── models/
│   │   ├── construction_aaw.py
│   │   ├── construction_aaw_line.py
│   │   ├── construction_aaw_surcharge_template.py
│   │   ├── project_project.py   (inherit: add aaw_ids)
│   │   └── contract_contract.py (inherit: add aaw_ids)
│   ├── views/
│   │   ├── construction_aaw_views.xml
│   │   ├── construction_aaw_line_views.xml
│   │   ├── construction_aaw_surcharge_template_views.xml
│   │   └── project_project_views.xml
│   ├── security/
│   │   └── ir.model.access.csv
│   ├── data/
│   │   └── aaw_sequence.xml
│   └── __manifest__.py
├── construction_sign/         # Generalized sign.mixin (future)
└── construction_surcharge/    # Surcharge templates (future, or in construction_aaw)
```

**Decision**: Keep surcharge templates and sign.mixin in `construction_aaw` for MVP. Extract to separate modules if they grow. The sign.mixin will be designed as a reusable abstract model from day one.

### Decision 3: ÄTA numbering per project

**Chosen**: Per-project sequence (`project.aaw_sequence_id` → `ir.sequence`)

```
ÄTA nr format: "ÄTA {seq}" where seq resets per project
Example: Project A → ÄTA 001, ÄTA 002; Project B → ÄTA 001, ÄTA 002
```

**Alternatives considered**: Global numbering — rejected because contractors organize by project, not globally. This matches Next Project and Hantverksdata behavior.

### Decision 4: State machine

```
draft ──→ submitted ──→ approved ──→ in_progress ──→ done ──→ invoiced ──→ closed
  │                      │                                                      │
  └──────────────────────┼──────────────────────────────────────────────────────┘
                         ▼
                      rejected                    cancelled (from draft/submitted)
```

**Transitions**:
| From | To | Trigger | Guard |
|---|---|---|---|
| draft | submitted | User action "Send to customer" | description filled, lines exist |
| submitted | approved | User action "Customer approved" | — |
| submitted | rejected | User action "Customer rejected" | customer_comment required |
| approved | in_progress | User action "Start work" | — |
| in_progress | done | User action "Mark complete" | — |
| done | invoiced | Auto when all billable lines invoiced | — |
| invoiced | closed | User action "Close ÄTA" | — |
| draft | cancelled | User action "Cancel" | — |
| submitted | cancelled | User action "Cancel" | — |

### Decision 5: sign.mixin design

**Chosen**: Abstract model `sign.mixin` that any model can inherit:

```python
class SignMixin(models.AbstractModel):
    _name = "sign.mixin"
    _description = "Mixin for models that support digital signing"

    sign_request_ids = fields.One2many("sign.oca.request", "res_id", 
                                        domain=[("res_model", "=", "...")])
    sign_request_count = fields.Integer(compute="_compute_sign_request_count")
    is_signed = fields.Boolean(compute="_compute_is_signed")

    def action_request_signature(self): ...
    def action_view_sign_requests(self): ...
    def _generate_sign_request(self): ...
```

The `sign.oca.request` model gets two new fields: `res_model` (Char) and `res_id` (Integer) — replacing the hardcoded `task_id` FK. This enables signing on any model without `sign_project_task`'s model-specific coupling.

## Data Model

```
┌──────────────────────────────────────────────────────────────────┐
│                     construction_aaw                             │
├──────────────────────────────────────────────────────────────────┤
│ PK  id                  INTEGER                                  │
│     name                CHAR        "ÄTA 003" (sequence)         │
│     project_id          M2O → project.project                    │
│     contract_id         M2O → contract.contract                  │
│     partner_id          M2O → res.partner                        │
│     partner_contact_id  M2O → res.partner                        │
│     description         HTML        uppdragsbeskrivning          │
│     aaw_type            SELECTION   ändring/tillägg/avgående     │
│     construction_type_id M2O → construction.aaw.type (optional)  │
│                                                                   │
│     compensation_method SELECTION   fixed_price/unit_price/      │
│                                     cost_plus                    │
│     estimated_amount    MONETARY    kalkylerat (exkl påslag)     │
│     surcharge_template_id M2O → aaw.surcharge.template           │
│     surcharge_amount    MONETARY    totalt påslag                │
│     offer_amount        MONETARY    = estimated + surcharge      │
│     agreed_amount       MONETARY    avtalat efter förhandling    │
│     cost_total          MONETARY    (compute) bokförd kostnad    │
│     revenue_total       MONETARY    (compute) bokförd intäkt     │
│     uninvoiced_amount   MONETARY    (compute) ej fakturerat      │
│     hide_surcharge      BOOLEAN     dölj påslag rapport/faktura  │
│     currency_id         M2O → res.currency                      │
│                                                                   │
│     state               SELECTION   draft/submitted/approved/    │
│                                     rejected/in_progress/done/   │
│                                     invoiced/closed/cancelled    │
│     notification_date   DATE        §9 underrättelse             │
│     written_order_date  DATE        §8 beställning               │
│     approved_date       DATE        kund godkände                │
│     completed_date      DATE        arbete klart                 │
│     invoice_date        DATE        senaste faktura              │
│     closed_date         DATE        slutreglerad                 │
│     time_extension_days INTEGER     tidsförlängning              │
│     time_extension_approved BOOLEAN                              │
│     customer_approved   BOOLEAN     portal-godkännande           │
│     customer_comment    TEXT                                      │
│                                                                   │
│     user_id             M2O → res.users                          │
│     tag_ids             M2M → aaw.tag (optional)                 │
│     internal_notes      HTML                                      │
│     is_invoiced         BOOLEAN     (compute)                    │
│                                                                   │
│ O2M order_line_ids      → construction.aaw.line                  │
│ O2M timesheet_ids       → account.analytic.line (domain filter)  │
│ M2M invoice_ids         → account.move                           │
│ O2M task_ids            → project.task (optional execution tasks) │
├──────────────────────────────────────────────────────────────────┤
│ FK  project_id, contract_id, partner_id, currency_id, etc.       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  construction.aaw.line                           │
├──────────────────────────────────────────────────────────────────┤
│ PK  id                  INTEGER                                  │
│ FK  aaw_id              M2O → construction.aaw                   │
│     sequence            INTEGER                                  │
│ FK  product_id          M2O → product.product                    │
│     name                CHAR                                      │
│ FK  account_id          M2O → account.account                    │
│ FK  uom_id              M2O → uom.uom                            │
│     estimated_quantity  FLOAT       kalkylerad mängd             │
│     executed_quantity   FLOAT       utförd mängd                 │
│     sold_quantity       FLOAT       fakturerad mängd             │
│     unit_price          MONETARY    á-pris till kund              │
│     cost_per_unit       MONETARY    kostnad/enhet                │
│     surcharge_percent   FLOAT       påslag %                     │
│     surcharge_amount    MONETARY    påslag kr (compute)          │
│     offer_amount        MONETARY    anbudsbelopp (compute)       │
│     cost_subtotal       MONETARY    totalkostnad (compute)       │
│     billable            BOOLEAN     debiterbar                   │
│     executed_date       DATE                                      │
│     comment             TEXT                                      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│               construction.aaw.surcharge.template                │
├──────────────────────────────────────────────────────────────────┤
│ PK  id                  INTEGER                                  │
│     name                CHAR        "Standardpåslag 15%"         │
│     surcharge_percent   FLOAT       default påslag %             │
│     company_id          M2O → res.company                        │
│     active              BOOLEAN                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Risks / Trade-offs

- **[Risk] Migration path for existing contract_aaw users** → Mitigation: `contract_aaw` stays installable but marked deprecated. New projects use `construction_aaw`. No auto-migration — manual conversion or script in Phase 2.
- **[Risk] sign.mixin requires schema change on sign.oca.request** → Mitigation: `sign_oca` is OCA — we add fields via a new module `sign_mixin` in odoo-sign repo that extends `sign.oca.request` with `res_model`/`res_id` generic reference. Existing `task_id` field remains for backward compat.
- **[Risk] Performance of per-project sequences** → Mitigation: `ir.sequence` with prefix scoped to project. Standard Odoo pattern, no known performance issues.
- **[Trade-off] Not reusing project.task for execution** → Tasks can still be linked via `task_ids` O2M for companies that want to use Odoo's task management for ÄTA execution. But the ÄTA itself is not a task.

## Open Questions

- Should surcharge templates be in `construction_aaw` or extracted to a shared `construction_surcharge` module? (Starting in `construction_aaw`, extract if reused)
- Should `construction.aaw.type` be a separate model or a selection field? (Separate model for customer-configurable types, matching Next Project)
