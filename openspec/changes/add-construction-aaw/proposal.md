## Why

Swedish construction companies working under AB04/ABT06 need proper ÄTA (Ändrings-, Tilläggs-, Avgående arbeten) handling — a legally regulated change order workflow with written notification (§9), customer approval (§8), pricing, execution tracking, and invoicing. Today, `contract_aaw` reduces this to a boolean flag (`is_aaw`) on `project.task`, which is insufficient for medium-to-large contractors. Next Project and Hantverksdata own this market with dedicated ÄTA modules. We need a first-class `construction.aaw` model to compete.

## What Changes

- **New module `construction_aaw`** in `odoo-construction` repo — standalone Odoo 18 module
- **New model `construction.aaw`** with full ABT06-compliant lifecycle: draft → submitted → approved/rejected → in_progress → done → invoiced → closed
- **New model `construction.aaw.line`** for order lines (materials, labor, surcharges per line)
- **New model `construction.aaw.surcharge.template`** for surcharge templates that can override per-line surcharges
- ÄTA numbering per project (ÄTA 001, ÄTA 002, ...)
- Replace signing with **generalized sign.mixin** (reusable across any model, not just project.task)
- Add `aaw_ids` relation on `project.project` and `contract.contract`
- **BREAKING**: Deprecate `contract_aaw` module. `project.task.is_aaw` becomes legacy.

## Capabilities

### New Capabilities

- `construction-aaw`: Core ÄTA/change order model with ABT06 lifecycle, per-project numbering, order lines with surcharges, cost/revenue tracking, and integration with project and contract
- `construction-aaw-surcharge`: Surcharge template management (påslagsmallar) that can override individual line surcharges, matching Next Project's model
- `sign-mixin`: Generalized digital signing mixin for Odoo models, replacing the model-specific `sign_project_task` with a reusable `sign.mixin` abstract model

### Modified Capabilities

<!-- No existing specs to modify — this is the first module in odoo-construction -->

## Impact

- **New repo**: `/usr/share/odoo-construction/construction_aaw/`
- **Depends on**: `project`, `contract`, `account`, `sale_management`, `sign_oca`
- **Replaces**: `contract_aaw` (odoo-contract), `sign_project_task` (odoo-sign) — both deprecated, not deleted (existing customers may use them)
- **Connects to**: `project.project` (new `aaw_ids` O2M), `contract.contract` (new `aaw_ids` O2M)
- **Phase 2 dependency**: SVA/prognos module will consume `construction.aaw` data for revenue recognition

## Non-goals

- SVA / successiv vinstavräkning (Phase 2)
- Kalkylimport (BidCon, MAP, Wikells) — Phase 2
- Projektdagbok — separate module
- KMA-pärm / egenkontroller — separate module using OCA mgmtsystem
- BEAst format integration
- ID06 / personalliggare
