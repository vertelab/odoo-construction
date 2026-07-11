## ADDED Requirements

### Requirement: Generic model reference on sign request
The system SHALL extend sign.oca.request with generic reference fields (res_model, res_id) enabling digital signing on any Odoo model, not just project.task.

#### Scenario: Create sign request for arbitrary model
- **WHEN** a sign request is created with res_model="construction.aaw" and res_id=42
- **THEN** the sign request SHALL be linked to the ÄTA with id 42

#### Scenario: Backward compatibility with task_id
- **WHEN** a sign request is created for project.task
- **THEN** task_id SHALL be set in addition to res_model/res_id for backward compatibility

### Requirement: Sign mixin abstract model
The system SHALL provide an abstract model sign.mixin that any Odoo model can inherit to gain signing capabilities.

#### Scenario: Model inherits sign.mixin
- **WHEN** construction.aaw inherits sign.mixin
- **THEN** it gains sign_request_ids, sign_request_count, is_signed fields
- **AND** it gains action_request_signature() and action_view_sign_requests() methods

#### Scenario: Request signature from mixin
- **WHEN** user calls action_request_signature() on an ÄTA with a partner_id
- **THEN** a sign.oca.request SHALL be created with the ÄTA's partner
- **AND** a notification email SHALL be sent to the partner

#### Scenario: Compute is_signed from sign requests
- **WHEN** all sign requests linked to a record are signed
- **THEN** is_signed SHALL be True

#### Scenario: View sign requests from record
- **WHEN** user clicks "View Sign Requests" on an ÄTA
- **THEN** an action window SHALL open showing all sign requests linked via res_model/res_id

### Requirement: Multiple signers per record
The system SHALL support multiple sign requests per record for scenarios requiring multiple signatures (e.g., customer + project manager + subcontractor).

#### Scenario: Multiple sign requests
- **WHEN** two sign requests are created for the same ÄTA with different partners
- **THEN** both SHALL appear in sign_request_ids
- **AND** is_signed SHALL only be True when ALL requests are signed
