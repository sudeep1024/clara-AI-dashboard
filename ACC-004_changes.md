# Changelog: ACC-004

**Generated:** 2026-03-04T05:28:29.034278+00:00
**Total changes:** 29

---

## Memo Changes (18)

### `memo._extracted_at` — *removed*
- Removed: `"2026-03-04T05:28:28.971081+00:00"`

### `memo._onboarding_extracted_at` — *added*
- Added: `"2026-03-04T05:28:28.971206+00:00"`

### `memo._pipeline` — *modified*
- Before: `"A"`
- After:  `"B"`

### `memo._previous_version` — *added*
- Added: `"v1"`

### `memo._source_file` — *modified*
- Before: `"ACC-004_demo.txt"`
- After:  `"ACC-004_onboarding.txt"`

### `memo._version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

### `memo.after_hours_flow_summary` — *modified*
- Before: `"Greet, confirm emergency, transfer to on-call electrician, fallback if transfer fails."`
- After:  `"Greet, confirm emergency (5 triggers), collect name/number, transfer to on-call 512-555-0183 then 512-555-0247 (30s each), if fail direct to 911 for life-safety risk or give 15-min callback. Spanish language callers supported."`

### `memo.call_transfer_rules.max_attempts` — *modified*
- Before: `null`
- After:  `2`

### `memo.call_transfer_rules.pre_transfer_message` — *modified*
- Before: `"I'm connecting you with our on-call electrician now."`
- After:  `"I'm connecting you with our on-call electrician now. Please hold."`

### `memo.call_transfer_rules.timeout_seconds` — *modified*
- Before: `null`
- After:  `30`

### `memo.call_transfer_rules.transfer_fail_message` — *modified*
- Before: `"I was unable to reach our on-call team. A technician will call you back."`
- After:  `"I was unable to reach our on-call team. If this is a life-safety emergency, please call 911 immediately. Otherwise, a technician will call you back within fifteen minutes."`

### `memo.emergency_definition` — *modified*
- Before: `["total power outage at commercial property", "exposed or sparking wiring", "hot or noisy electrical panel", "immediate electrical safety risk"]`
- After:  `["total power outage at commercial property", "exposed or sparking wiring", "hot or noisy electrical panel", "immediate electrical safety risk", "electrical fire smell or visible smoke near electrical equipment"]`

### `memo.emergency_routing_rules` — *modified*
- Before: `[{"order": 1, "contact": "on-call lead electrician (rotating)", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call electrician", "phone": "512-555-0183", "timeout_seconds": 30}, {"order": 2, "contact": "backup on-call electrician", "phone": "512-555-0247", "timeout_seconds": 30}]`

### `memo.integration_constraints` — *modified*
- Before: `["do not create Jobber jobs automatically without human review"]`
- After:  `["do not create Jobber jobs automatically \u2013 human review required", "never reveal on-call technician names to callers \u2013 say 'our on-call technician'", "never provide price estimates or quotes on calls \u2013 redirect to business hours"]`

### `memo.notes` — *modified*
- Before: `"Demo call. On-call rotation numbers not yet provided. Spanish language mentioned as possible need."`
- After:  `"Spanish language support confirmed. On-call names never disclosed to callers."`

### `memo.office_address` — *modified*
- Before: `null`
- After:  `"512 West Riverside Drive, Austin, Texas 78704"`

### `memo.office_hours_flow_summary` — *modified*
- Before: `"Greet, collect purpose, route appropriately, take message for non-urgent."`
- After:  `"Greet, collect purpose, collect name and number, route or message. No quotes. No on-call names disclosed."`

### `memo.questions_or_unknowns` — *modified*
- Before: `["What are the on-call electrician phone numbers?", "What is the office address?", "Is Spanish language support required?", "How many transfer attempts?"]`
- After:  `[]`

## Spec Changes (10)

### `spec.call_transfer_protocol.max_attempts` — *modified*
- Before: `null`
- After:  `2`

### `spec.call_transfer_protocol.pre_transfer_message` — *modified*
- Before: `"I'm connecting you with our on-call electrician now."`
- After:  `"I'm connecting you with our on-call electrician now. Please hold."`

### `spec.call_transfer_protocol.routing_order` — *modified*
- Before: `[{"order": 1, "contact": "on-call lead electrician (rotating)", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call electrician", "phone": "512-555-0183", "timeout_seconds": 30}, {"order": 2, "contact": "backup on-call electrician", "phone": "512-555-0247", "timeout_seconds": 30}]`

### `spec.call_transfer_protocol.timeout_seconds` — *modified*
- Before: `null`
- After:  `30`

### `spec.fallback_protocol.message` — *modified*
- Before: `"I was unable to reach our on-call team. A technician will call you back."`
- After:  `"I was unable to reach our on-call team. If this is a life-safety emergency, please call 911 immediately. Otherwise, a technician will call you back within fifteen minutes."`

### `spec.integration_constraints` — *modified*
- Before: `["do not create Jobber jobs automatically without human review"]`
- After:  `["do not create Jobber jobs automatically \u2013 human review required", "never reveal on-call technician names to callers \u2013 say 'our on-call technician'", "never provide price estimates or quotes on calls \u2013 redirect to business hours"]`

### `spec.key_variables.emergency_routing` — *modified*
- Before: `[{"order": 1, "contact": "on-call lead electrician (rotating)", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call electrician", "phone": "512-555-0183", "timeout_seconds": 30}, {"order": 2, "contact": "backup on-call electrician", "phone": "512-555-0247", "timeout_seconds": 30}]`

### `spec.key_variables.office_address` — *modified*
- Before: `null`
- After:  `"512 West Riverside Drive, Austin, Texas 78704"`

### `spec.questions_or_unknowns` — *modified*
- Before: `["What are the on-call electrician phone numbers?", "What is the office address?", "Is Spanish language support required?", "How many transfer attempts?"]`
- After:  `[]`

### `spec.version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

## System Prompt

Prompt **regenerated** from updated memo. See `v2/agent_spec.json`.
