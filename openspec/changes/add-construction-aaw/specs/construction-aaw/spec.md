## ADDED Requirements

### Requirement: ÄTA lifecycle management
The system SHALL manage ÄTA (change orders) through a defined state machine matching ABT06 §§ 3–9 requirements, with states: draft, submitted, approved, rejected, in_progress, done, invoiced, closed, cancelled.

#### Scenario: Create ÄTA in draft state
- **WHEN** user creates a new ÄTA on a project
- **THEN** the ÄTA is created in "draft" state with auto-generated per-project name "ÄTA 001"

#### Scenario: Submit ÄTA to customer
- **WHEN** user triggers "Send to customer" on a draft ÄTA
- **THEN** state transitions to "submitted" and notification_date is set to current date

#### Scenario: Customer approves ÄTA
- **WHEN** user triggers "Customer approved" on a submitted ÄTA
- **THEN** state transitions to "approved", approved_date and written_order_date are set

#### Scenario: Customer rejects ÄTA
- **WHEN** user triggers "Customer rejected" on a submitted ÄTA
- **THEN** state transitions to "rejected" and customer_comment field is required

#### Scenario: Start execution
- **WHEN** user triggers "Start work" on an approved ÄTA
- **THEN** state transitions to "in_progress"

#### Scenario: Mark complete
- **WHEN** user triggers "Mark complete" on an in_progress ÄTA
- **THEN** state transitions to "done" and completed_date is set

#### Scenario: Full invoicing
- **WHEN** all billable order lines on a "done" ÄTA are invoiced
- **THEN** state automatically transitions to "invoiced" and invoice_date is set

#### Scenario: Close ÄTA
- **WHEN** user triggers "Close" on an invoiced ÄTA
- **THEN** state transitions to "closed" and closed_date is set

#### Scenario: Cancel from draft or submitted
- **WHEN** user triggers "Cancel" on a draft or submitted ÄTA
- **THEN** state transitions to "cancelled"

### Requirement: ÄTA types
The system SHALL support classifying ÄTA as one of three ABT06 types: ändring (modification), tillägg (addition), avgående (removal).

#### Scenario: Set ÄTA type during creation
- **WHEN** user creates a new ÄTA
- **THEN** they SHALL be able to select ändring, tillägg, or avgående from the aaw_type field

### Requirement: Per-project ÄTA numbering
The system SHALL assign ÄTA numbers sequentially per project using the format "ÄTA <seq>" where the sequence resets for each project.

#### Scenario: First ÄTA on a project
- **WHEN** the first ÄTA is created on a project with no previous ÄTAs
- **THEN** its name is "ÄTA 001"

#### Scenario: Second ÄTA on same project
- **WHEN** a second ÄTA is created on the same project
- **THEN** its name is "ÄTA 002"

#### Scenario: First ÄTA on different project
- **WHEN** the first ÄTA is created on a different project
- **THEN** its name is "ÄTA 001" (independent sequence)

### Requirement: Compensation methods
The system SHALL support three compensation methods: fixed_price (fast pris), unit_price (à-pris), cost_plus (löpande räkning).

#### Scenario: Select compensation method
- **WHEN** user creates or edits an ÄTA
- **THEN** they SHALL select one of fixed_price, unit_price, or cost_plus

#### Scenario: Fixed price amount tracking
- **WHEN** compensation method is fixed_price
- **THEN** the agreed_amount field SHALL be used for the fixed contract sum

### Requirement: Order lines management
The system SHALL allow adding multiple order lines (construction.aaw.line) to each ÄTA, where each line has estimated and executed quantities, unit price, cost per unit, surcharge, and billable flag.

#### Scenario: Add order line
- **WHEN** user adds an order line to a draft ÄTA
- **THEN** the line appears in the order line list with default sequence

#### Scenario: Calculate line amounts
- **WHEN** an order line has quantity, unit_price, surcharge_percent
- **THEN** surcharge_amount SHALL compute as unit_price * quantity * surcharge_percent / 100
- **AND** offer_amount SHALL compute as unit_price * quantity + surcharge_amount

#### Scenario: Mark line as billable
- **WHEN** user sets billable=True on an order line
- **THEN** the line SHALL be included in ÄTA invoicing

#### Scenario: Non-billable line exclusion
- **WHEN** an order line has billable=False
- **THEN** it SHALL NOT be included in invoicing calculations

### Requirement: Cost and revenue tracking
The system SHALL compute total cost, revenue, and uninvoiced amount for each ÄTA based on its order lines and related invoices.

#### Scenario: Compute total cost
- **WHEN** order lines have executed_quantity and cost_per_unit
- **THEN** cost_total SHALL sum executed_quantity * cost_per_unit across all lines

#### Scenario: Compute uninvoiced amount
- **WHEN** billable lines have been executed but not invoiced
- **THEN** uninvoiced_amount SHALL be the sum of (executed_quantity * unit_price + surcharge) for unbilled billable lines

#### Scenario: Auto-detect fully invoiced
- **WHEN** uninvoiced_amount equals 0 and state is "done"
- **THEN** is_invoiced SHALL be True

### Requirement: Project and contract integration
The system SHALL expose ÄTA lists on both project.project and contract.contract via One2many relations.

#### Scenario: View ÄTAs on project
- **WHEN** user opens a project form with associated ÄTAs
- **THEN** the aaw_ids field SHALL display all ÄTAs for that project

#### Scenario: View ÄTAs on contract
- **WHEN** user opens a contract form with associated ÄTAs
- **THEN** the aaw_ids field SHALL display all ÄTAs for that contract

#### Scenario: Stat button on project
- **WHEN** user views a project with ÄTAs
- **THEN** a stat button SHALL show ÄTA count with total offer_amount

### Requirement: ABT06 time extension tracking
The system SHALL support tracking requested and approved time extensions (tidsförlängning) as required by ABT06 § 6.

#### Scenario: Request time extension
- **WHEN** user sets time_extension_days on an approved or in_progress ÄTA
- **THEN** the value SHALL be stored without auto-approval

#### Scenario: Approve time extension
- **WHEN** user sets time_extension_approved to True
- **THEN** the approved time extension SHALL be visible in ÄTA reports

### Requirement: Internal notes and customer comments
The system SHALL maintain separate fields for internal notes (internal_notes, HTML) and customer-facing comments (customer_comment, plain text).

#### Scenario: Internal notes hidden from customer
- **WHEN** user writes notes in internal_notes field
- **THEN** they SHALL NOT appear in customer-facing documents or portal views

#### Scenario: Customer comment on portal approval
- **WHEN** customer approves via portal and adds a comment
- **THEN** the comment SHALL be stored in customer_comment and customer_approved set to True
