## ADDED Requirements

### Requirement: Surcharge template model
The system SHALL provide a surcharge template model (construction.aaw.surcharge.template) with name, surcharge percentage, company, and active flag.

#### Scenario: Create surcharge template
- **WHEN** user creates a new surcharge template with name "Standard 15%" and surcharge_percent 15.0
- **THEN** the template is saved and available for ÄTA assignment

#### Scenario: Deactivate template
- **WHEN** user sets active=False on a template
- **THEN** the template SHALL not appear in selection lists but existing ÄTAs using it remain unchanged

### Requirement: Template overrides per-line surcharges
The system SHALL apply the surcharge template percentage to all order lines when assigned to an ÄTA, overriding individual line surcharge_percent values.

#### Scenario: Apply template to ÄTA
- **WHEN** user selects a surcharge template with 15% on an ÄTA
- **THEN** all order lines SHALL use 15% surcharge for amount calculations regardless of individual surcharge_percent values

#### Scenario: Remove template from ÄTA
- **WHEN** user removes the surcharge template from an ÄTA
- **THEN** order lines SHALL revert to their individual surcharge_percent values

#### Scenario: Template surcharge reflected in offer_amount
- **WHEN** a surcharge template of 15% is applied to an ÄTA with estimated_amount 100000
- **THEN** surcharge_amount SHALL be 15000 and offer_amount SHALL be 115000
