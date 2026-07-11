## 1. Module Scaffold

- [x] 1.1 Create `construction_aaw` module structure with `__manifest__.py`, `__init__.py`, and directory layout (models/, views/, security/, data/, i18n/)
- [x] 1.2 Define `__manifest__.py` with dependencies: `project`, `contract`, `account`, `sale_management`, `sign_oca`, `mail`
- [x] 1.3 Create `security/ir.model.access.csv` with CRUD rules for `construction.aaw`, `construction.aaw.line`, `construction.aaw.surcharge.template`
- [x] 1.4 Create per-project `ir.sequence` in `data/aaw_sequence.xml` with prefix "ÄTA " and project-scoped sequence

## 2. Core Data Models

- [x] 2.1 Implement `construction.aaw` model with all fields: identification, financial, state, ABT06, relations (as specified in design.md)
- [x] 2.2 Implement `construction.aaw` state machine with transitions: draft→submitted→approved/rejected→in_progress→done→invoiced→closed, plus cancelled from draft/submitted
- [x] 2.3 Implement `construction.aaw` computed fields: `cost_total`, `revenue_total`, `uninvoiced_amount`, `is_invoiced`
- [x] 2.4 Implement `construction.aaw.line` model with quantity, pricing, surcharge, billable fields and computed amounts
- [x] 2.5 Implement `construction.aaw.surcharge.template` model with name, surcharge_percent, company_id, active
- [x] 2.6 Add `aaw_ids` One2many on `project.project` (inherit) with computed `aaw_count` and `aaw_amount_total`
- [x] 2.7 Add `aaw_ids` One2many on `contract.contract` (inherit) with computed `aaw_count`

## 3. Business Logic

- [x] 3.1 Auto-assign sequence name on create per project scope
- [x] 3.2 Implement surcharge template application: when template assigned to ÄTA, override all line surcharges; on removal, revert to individual values
- [x] 3.3 Implement order line amount computation: `surcharge_amount = estimated_quantity * unit_price * surcharge_percent / 100` (or template-driven), `offer_amount = estimated_quantity * unit_price + surcharge_amount`
- [x] 3.4 Implement state transition guards: description required for submit, customer_comment required for reject
- [x] 3.5 Auto-transition to "invoiced" when all billable lines are invoiced and state is "done"

## 4. Views — ÄTA

- [x] 4.1 Create `construction.aaw` form view with header (state, buttons), sheet (all fields organized in groups), and chatter
- [x] 4.2 Create `construction.aaw` tree view with name, partner, aaw_type, state, estimated_amount, offer_amount
- [x] 4.3 Create `construction.aaw` search view with filters by state, project, partner, aaw_type
- [x] 4.4 Create `construction.aaw` kanban view with state-colored cards showing name, partner, amounts
- [x] 4.5 Add action window and menu items under Project > ÄTA (or dedicated menu)

## 5. Views — Order Lines & Surcharge Templates

- [x] 5.1 Create `construction.aaw.line` tree view (editable inline within ÄTA form)
- [x] 5.2 Create `construction.aaw.surcharge.template` form view
- [x] 5.3 Create `construction.aaw.surcharge.template` tree view with name, surcharge_percent, active
- [x] 5.4 Add action window and menu items for surcharge templates under Configuration

## 6. Views — Project & Contract Integration

- [x] 6.1 Add ÄTA stat button on `project.project` form view showing count and total
- [x] 6.2 Add ÄTA notebook tab on `project.project` form view with embedded tree view
- [x] 6.3 Add ÄTA stat button on `contract.contract` form view

## 7. Sign Mixin

- [x] 7.1 Extend `sign.oca.request` model with `res_model` (Char) and `res_id` (Integer) fields for generic model reference
- [x] 7.2 Implement `sign.mixin` abstract model with `sign_request_ids`, `sign_request_count`, `is_signed` fields
- [x] 7.3 Implement `action_request_signature()` method on mixin: create sign request, send notification email
- [x] 7.4 Implement `action_view_sign_requests()` method on mixin: open filtered sign request view
- [x] 7.5 Implement `_compute_is_signed()`: True when all associated sign requests are signed
- [x] 7.6 Add `sign.mixin` inheritance to `construction.aaw`
- [x] 7.7 Ensure backward compatibility: existing `task_id` field on `sign.oca.request` remains functional

## 8. Security & Access Control

- [x] 8.1 Define access groups in `security/ir.model.access.csv`: user (read own project ÄTA), manager (CRUD all)
- [x] 8.2 Add record rules: users see ÄTAs only for their assigned projects
- [x] 8.3 Add field-level security on financial fields (estimated_amount, agreed_amount) — only managers edit

## 9. Swedish Translations

- [x] 9.1 Create `i18n/sv.po` with Swedish translations for all model fields, views, and selection values
- [x] 9.2 Translate state values: draft=Utkast, submitted=Inskickad, approved=Godkänd, rejected=Avvisad, in_progress=Pågående, done=Klar, invoiced=Fakturerad, closed=Avslutad, cancelled=Avbruten
- [x] 9.3 Translate aaw_type values: ändring=Ändring, tillägg=Tillägg, avgående=Avgående
- [x] 9.4 Translate compensation_method: fixed_price=Fast pris, unit_price=À-pris, cost_plus=Löpande räkning

## 10. Testing & Documentation

- [x] 10.1 Write unit tests for state machine transitions and guards
- [x] 10.2 Write unit tests for computed fields (cost_total, revenue_total, uninvoiced_amount)
- [x] 10.3 Write unit tests for surcharge template override/revert logic
- [x] 10.4 Write unit tests for per-project sequence numbering
- [x] 10.5 Create `README.md` for `construction_aaw` module with feature overview, dependencies, and configuration steps
- [x] 10.6 Test installation on clean Odoo 18 database and verify no conflicts with contract_aaw coexistence
