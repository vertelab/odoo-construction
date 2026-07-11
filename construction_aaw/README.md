# Construction: ÄTA (Change Orders)

Odoo 18 module for managing Ändrings-, Tilläggs- och Avgående arbeten (ÄTA) — Swedish construction change orders — compliant with AB04/ABT06.

## Features

- **Full ÄTA lifecycle**: Draft → Submitted → Approved/Rejected → In Progress → Done → Invoiced → Closed
- **Per-project numbering** (ÄTA 001, ÄTA 002, ...)
- **Order lines** with quantities, unit prices, costs, surcharges
- **Surcharge templates** that can override per-line surcharges (matching Next Project's model)
- **Digital signing** via `sign.mixin` (generalized from `sign_project_task`)
- **ABT06 compliance**: §9 notification date, §8 written order date, time extension tracking
- **Seamless integration**: Embedded in project and contract forms

## Dependencies

- `project`
- `contract`
- `account`
- `sale_management`
- `sign_oca`
- `mail`

## Installation

1. Clone `odoo-construction` into your addons path
2. Update the module list
3. Install "Construction: ÄTA (Change Orders)"

## Configuration

### Surcharge Templates
Go to **Construction → Configuration → Surcharge Templates** to create templates with default surcharge percentages. Assign templates to ÄTAs to override individual line surcharges.

### ÄTA Sequence
The per-project sequence "ÄTA xxx" is configured in Settings → Technical → Sequences & Identifiers → Sequences → Construction ÄTA Sequence.

## Usage

### Creating an ÄTA
1. Open a project
2. Go to the **ÄTA** tab or click the ÄTA stat button
3. Click **Create**
4. Fill in the description, select ÄTA type and compensation method
5. Add order lines with quantities, prices, and surcharges

### Workflow
1. **Draft** → Prepare the ÄTA internally
2. **Submit** → Send to customer for approval (§9 notification)
3. **Approve/Reject** → Customer decides (§8 written order)
4. **Start Work** → Begin execution
5. **Mark Done** → Work completed
6. **Invoice** → Create invoice for billable lines
7. **Close** → Final settlement

### Signing
Click **Request Signature** on any ÄTA to send a digital signing request to the customer via `sign_oca`.

## Tests

```bash
# Run tests
odoo-bin --addons-path=/usr/share/odoo-construction -d test_db --test-enable -i construction_aaw --stop-after-init
```

## License

AGPL-3.0 — Copyright Vertel Sverige AB
