# Changelog: ACC-003

**Generated:** 2026-03-04T05:28:28.983090+00:00
**Total changes:** 29

---

## Memo Changes (19)

### `memo._extracted_at` — *removed*
- Removed: `"2026-03-04T05:28:28.971076+00:00"`

### `memo._onboarding_extracted_at` — *added*
- Added: `"2026-03-04T05:28:28.971101+00:00"`

### `memo._pipeline` — *modified*
- Before: `"A"`
- After:  `"B"`

### `memo._previous_version` — *added*
- Added: `"v1"`

### `memo._source_file` — *modified*
- Before: `"ACC-003_demo.txt"`
- After:  `"ACC-003_onboarding.txt"`

### `memo._version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

### `memo.after_hours_flow_summary` — *modified*
- Before: `"Greet, triage emergency vs non-emergency, transfer for emergency, collect info for non-emergency."`
- After:  `"Greet, ask purpose, determine emergency (5 triggers), collect name/number/property address, attempt 3 transfers (dispatcher 206-555-0452 \u2192 Tom 206-555-0819 \u2192 Ray 206-555-0631, 30s each), if all fail confirm 20-min callback."`

### `memo.business_hours.notes` — *modified*
- Before: `"Closed weekends but accepts emergency calls"`
- After:  `"Closed weekends but emergency calls accepted"`

### `memo.call_transfer_rules.max_attempts` — *modified*
- Before: `null`
- After:  `3`

### `memo.call_transfer_rules.timeout_seconds` — *modified*
- Before: `null`
- After:  `30`

### `memo.call_transfer_rules.transfer_fail_message` — *modified*
- Before: `"I was unable to reach our on-call team. A technician will call you back."`
- After:  `"I'm sorry, I wasn't able to reach our on-call team directly. Your information has been logged and a technician will call you back within twenty minutes. Is the location safe to remain at?"`

### `memo.emergency_definition` — *modified*
- Before: `["complete system failure in commercial kitchen", "no heat in freezing weather", "CO detector triggered"]`
- After:  `["complete system failure in commercial kitchen", "no heat in freezing weather", "CO detector triggered", "flooding from HVAC drain line or condensate overflow inside building", "total cooling failure at data center or server room"]`

### `memo.emergency_routing_rules` — *modified*
- Before: `[{"order": 1, "contact": "on-call dispatcher", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call dispatcher", "phone": "206-555-0452", "timeout_seconds": 30}, {"order": 2, "contact": "service manager", "phone": "206-555-0819", "timeout_seconds": 30}, {"order": 3, "contact": "backup technician", "phone": "206-555-0631", "timeout_seconds": 30}]`

### `memo.integration_constraints` — *modified*
- Before: `["do not create jobs in ServiceTitan without human review"]`
- After:  `["do not auto-create jobs in ServiceTitan \u2013 dispatcher review required"]`

### `memo.non_emergency_routing_rules.collect_fields` — *modified*
- Before: `["name", "phone", "description"]`
- After:  `["name", "phone", "property_address", "description"]`

### `memo.notes` — *modified*
- Before: `"Demo call. On-call number and exact routing not yet confirmed."`
- After:  `"Three-level emergency routing confirmed. 20-min callback window."`

### `memo.office_address` — *modified*
- Before: `null`
- After:  `"8300 Aurora Avenue North, Suite 200, Seattle, Washington 98103"`

### `memo.office_hours_flow_summary` — *modified*
- Before: `"Greet, understand purpose, collect name and number, route or take message."`
- After:  `"Greet, collect purpose, collect name and number, route or take message. No quotes or pricing on calls."`

### `memo.questions_or_unknowns` — *modified*
- Before: `["What is the dispatcher on-call number?", "What is the office address?", "How many transfer attempts before fallback?"]`
- After:  `["Spanish language support \u2013 flagged for future"]`

## Spec Changes (9)

### `spec.call_transfer_protocol.max_attempts` — *modified*
- Before: `null`
- After:  `3`

### `spec.call_transfer_protocol.routing_order` — *modified*
- Before: `[{"order": 1, "contact": "on-call dispatcher", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call dispatcher", "phone": "206-555-0452", "timeout_seconds": 30}, {"order": 2, "contact": "service manager", "phone": "206-555-0819", "timeout_seconds": 30}, {"order": 3, "contact": "backup technician", "phone": "206-555-0631", "timeout_seconds": 30}]`

### `spec.call_transfer_protocol.timeout_seconds` — *modified*
- Before: `null`
- After:  `30`

### `spec.fallback_protocol.message` — *modified*
- Before: `"I was unable to reach our on-call team. A technician will call you back."`
- After:  `"I'm sorry, I wasn't able to reach our on-call team directly. Your information has been logged and a technician will call you back within twenty minutes. Is the location safe to remain at?"`

### `spec.integration_constraints` — *modified*
- Before: `["do not create jobs in ServiceTitan without human review"]`
- After:  `["do not auto-create jobs in ServiceTitan \u2013 dispatcher review required"]`

### `spec.key_variables.emergency_routing` — *modified*
- Before: `[{"order": 1, "contact": "on-call dispatcher", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "on-call dispatcher", "phone": "206-555-0452", "timeout_seconds": 30}, {"order": 2, "contact": "service manager", "phone": "206-555-0819", "timeout_seconds": 30}, {"order": 3, "contact": "backup technician", "phone": "206-555-0631", "timeout_seconds": 30}]`

### `spec.key_variables.office_address` — *modified*
- Before: `null`
- After:  `"8300 Aurora Avenue North, Suite 200, Seattle, Washington 98103"`

### `spec.questions_or_unknowns` — *modified*
- Before: `["What is the dispatcher on-call number?", "What is the office address?", "How many transfer attempts before fallback?"]`
- After:  `["Spanish language support \u2013 flagged for future"]`

### `spec.version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

## System Prompt

Prompt **regenerated** from updated memo. See `v2/agent_spec.json`.
