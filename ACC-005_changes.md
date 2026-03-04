# Changelog: ACC-005

**Generated:** 2026-03-04T05:28:29.038779+00:00
**Total changes:** 28

---

## Memo Changes (18)

### `memo._extracted_at` — *removed*
- Removed: `"2026-03-04T05:28:28.971085+00:00"`

### `memo._onboarding_extracted_at` — *added*
- Added: `"2026-03-04T05:28:28.971216+00:00"`

### `memo._pipeline` — *modified*
- Before: `"A"`
- After:  `"B"`

### `memo._previous_version` — *added*
- Added: `"v1"`

### `memo._source_file` — *modified*
- Before: `"ACC-005_demo.txt"`
- After:  `"ACC-005_onboarding.txt"`

### `memo._version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

### `memo.after_hours_flow_summary` — *modified*
- Before: `"Greet, determine if active emergency, collect name/number/address, transfer to on-call, fallback if fail."`
- After:  `"Greet, ask purpose, determine emergency (5 triggers), collect name/number/address (partial address accepted), transfer to on-call 773-555-0388 then owner 773-555-0194 (30s each), if fail give 15-min contact assurance with water shutoff guidance if applicable. Inspection calls = non-emergency path only."`

### `memo.call_transfer_rules.max_attempts` — *modified*
- Before: `null`
- After:  `2`

### `memo.call_transfer_rules.timeout_seconds` — *modified*
- Before: `null`
- After:  `30`

### `memo.call_transfer_rules.transfer_fail_message` — *modified*
- Before: `"I was unable to reach our team. A technician will call you back within fifteen minutes."`
- After:  `"I was unable to reach our team directly. Please remain calm. A technician will call you back within fifteen minutes. In the meantime, if water is actively flowing, locate and shut off the main water supply if it is safe to do so."`

### `memo.emergency_definition` — *modified*
- Before: `["active water discharge (head activated)", "dry pipe system trip", "backflow preventer failure with contamination risk"]`
- After:  `["active water discharge (sprinkler head activated)", "dry pipe system trip", "backflow preventer failure with contamination risk", "fire suppression system activation in commercial kitchen", "cracked or burst main riser"]`

### `memo.emergency_routing_rules` — *modified*
- Before: `[{"order": 1, "contact": "on-call technician (shared phone)", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call technician (shared rotation phone)", "phone": "773-555-0388", "timeout_seconds": 30}, {"order": 2, "contact": "owner", "phone": "773-555-0194", "timeout_seconds": 30}]`

### `memo.integration_constraints` — *modified*
- Before: `["never create sprinkler jobs in ServiceTrade", "do not create any job automatically without human review"]`
- After:  `["never create sprinkler jobs in ServiceTrade \u2013 this includes all sprinkler and fire suppression job types", "inspection scheduling requests may be logged as leads only \u2013 not created as jobs", "never discuss ServiceTrade job status \u2013 redirect to business hours", "inspection calls after hours are non-emergency \u2013 collect info and follow up next business day only"]`

### `memo.non_emergency_routing_rules.collect_fields` — *modified*
- Before: `["name", "phone", "description"]`
- After:  `["name", "phone", "property_address", "description"]`

### `memo.notes` — *modified*
- Before: `"Demo call. Client emphatic about not creating ServiceTrade jobs automatically."`
- After:  `"Emphatic constraint: no ServiceTrade job creation ever. Partial address ok for emergencies. Inspections = non-emergency after hours."`

### `memo.office_address` — *modified*
- Before: `null`
- After:  `"3741 North Kimball Avenue, Chicago, Illinois 60618"`

### `memo.office_hours_flow_summary` — *modified*
- Before: `"Greet, understand purpose, collect info, route or take message."`
- After:  `"Greet, collect purpose, collect info, route or take message. Do not create ServiceTrade jobs."`

### `memo.questions_or_unknowns` — *modified*
- Before: `["What is the on-call phone number?", "What is the office address?", "What is the exact transfer timeout?"]`
- After:  `[]`

## Spec Changes (9)

### `spec.call_transfer_protocol.max_attempts` — *modified*
- Before: `null`
- After:  `2`

### `spec.call_transfer_protocol.routing_order` — *modified*
- Before: `[{"order": 1, "contact": "on-call technician (shared phone)", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call technician (shared rotation phone)", "phone": "773-555-0388", "timeout_seconds": 30}, {"order": 2, "contact": "owner", "phone": "773-555-0194", "timeout_seconds": 30}]`

### `spec.call_transfer_protocol.timeout_seconds` — *modified*
- Before: `null`
- After:  `30`

### `spec.fallback_protocol.message` — *modified*
- Before: `"I was unable to reach our team. A technician will call you back within fifteen minutes."`
- After:  `"I was unable to reach our team directly. Please remain calm. A technician will call you back within fifteen minutes. In the meantime, if water is actively flowing, locate and shut off the main water supply if it is safe to do so."`

### `spec.integration_constraints` — *modified*
- Before: `["never create sprinkler jobs in ServiceTrade", "do not create any job automatically without human review"]`
- After:  `["never create sprinkler jobs in ServiceTrade \u2013 this includes all sprinkler and fire suppression job types", "inspection scheduling requests may be logged as leads only \u2013 not created as jobs", "never discuss ServiceTrade job status \u2013 redirect to business hours", "inspection calls after hours are non-emergency \u2013 collect info and follow up next business day only"]`

### `spec.key_variables.emergency_routing` — *modified*
- Before: `[{"order": 1, "contact": "on-call technician (shared phone)", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call technician (shared rotation phone)", "phone": "773-555-0388", "timeout_seconds": 30}, {"order": 2, "contact": "owner", "phone": "773-555-0194", "timeout_seconds": 30}]`

### `spec.key_variables.office_address` — *modified*
- Before: `null`
- After:  `"3741 North Kimball Avenue, Chicago, Illinois 60618"`

### `spec.questions_or_unknowns` — *modified*
- Before: `["What is the on-call phone number?", "What is the office address?", "What is the exact transfer timeout?"]`
- After:  `[]`

### `spec.version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

## System Prompt

Prompt **regenerated** from updated memo. See `v2/agent_spec.json`.
