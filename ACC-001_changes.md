# Changelog: ACC-001

**Generated:** 2026-03-04T05:28:28.974808+00:00
**Total changes:** 39

---

## Memo Changes (25)

### `memo._extracted_at` — *removed*
- Removed: `"2026-03-04T05:28:28.971046+00:00"`

### `memo._onboarding_extracted_at` — *added*
- Added: `"2026-03-04T05:28:28.971091+00:00"`

### `memo._pipeline` — *modified*
- Before: `"A"`
- After:  `"B"`

### `memo._previous_version` — *added*
- Added: `"v1"`

### `memo._source_file` — *modified*
- Before: `"ACC-001_demo.txt"`
- After:  `"ACC-001_onboarding.txt"`

### `memo._version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

### `memo.after_hours_flow_summary` — *modified*
- Before: `"Greet caller, determine if emergency (sprinkler/suppression/alarm), attempt transfer to on-call tech, if fail assure callback."`
- After:  `"Greet, state office closed and provide hours, ask purpose, confirm if emergency (5 defined triggers), collect name/number/address, attempt transfer (Sandra 303-555-0187 then Marcus 303-555-0294, 30s each), if fail assure 15-minute callback and confirm callback number."`

### `memo.business_hours.days` — *modified*
- Before: `["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]`
- After:  `["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]`

### `memo.business_hours.end` — *modified*
- Before: `"17:00"`
- After:  `"17:30"`

### `memo.business_hours.notes` — *modified*
- Before: `"Approximate from demo"`
- After:  `"Saturday 08:00\u201312:00 only"`

### `memo.business_hours.start` — *modified*
- Before: `"08:00"`
- After:  `"07:30"`

### `memo.call_transfer_rules.max_attempts` — *modified*
- Before: `null`
- After:  `2`

### `memo.call_transfer_rules.pre_transfer_message` — *modified*
- Before: `"Please hold while I connect you with our team."`
- After:  `"I'm going to connect you with our emergency dispatch now. Please stay on the line."`

### `memo.call_transfer_rules.timeout_seconds` — *modified*
- Before: `null`
- After:  `30`

### `memo.call_transfer_rules.transfer_fail_message` — *modified*
- Before: `"I was unable to reach our team. Someone will call you back."`
- After:  `"I wasn't able to reach our team right now. A technician will call you back within fifteen minutes. Please stay somewhere safe and do not attempt to fix the issue yourself."`

### `memo.emergency_definition` — *modified*
- Before: `["sprinkler head discharging", "fire suppression system activation", "active fire alarm triggering the system"]`
- After:  `["sprinkler head discharging", "fire suppression system activation", "active fire alarm triggering the system", "dry pipe system trip", "flooded pipe section"]`

### `memo.emergency_routing_rules` — *modified*
- Before: `[{"order": 1, "contact": "dispatch coordinator", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "dispatch coordinator", "phone": "303-555-0187", "timeout_seconds": 30}, {"order": 2, "contact": "operations manager", "phone": "303-555-0294", "timeout_seconds": 30}]`

### `memo.integration_constraints` — *modified*
- Before: `["do not create jobs in ServiceTrade automatically"]`
- After:  `["never create jobs in ServiceTrade \u2013 human review required for all new jobs", "do not engage with ServiceTrade job status inquiries \u2013 redirect to business hours"]`

### `memo.non_emergency_routing_rules.message_to_caller` — *modified*
- Before: `"We will follow up during business hours."`
- After:  `"We will follow up next business day."`

### `memo.non_emergency_routing_rules.notify_method` — *modified*
- Before: `"none"`
- After:  `"email"`

### `memo.non_emergency_routing_rules.notify_target` — *modified*
- Before: `null`
- After:  `"dispatch@blueskyfireprotection.com"`

### `memo.notes` — *modified*
- Before: `"Demo call - directional info only. Routing numbers not yet provided."`
- After:  `"Onboarding confirmed. No agent names mentioned to callers. Saturday hours confirmed."`

### `memo.office_address` — *modified*
- Before: `null`
- After:  `"4820 Havana Street, Denver, Colorado 80239"`

### `memo.office_hours_flow_summary` — *modified*
- Before: `"Greet caller, collect name and number, route to appropriate team or take message."`
- After:  `"Greet, ask purpose, collect name and number, route to appropriate team. For emergencies during hours, proceed with emergency transfer protocol."`

### `memo.questions_or_unknowns` — *modified*
- Before: `["What is the exact on-call dispatch phone number?", "What is the office address?", "What are the exact business hours?", "Is Spanish language support needed?"]`
- After:  `["Spanish language support \u2013 flagged for future enhancement"]`

## Spec Changes (13)

### `spec.call_transfer_protocol.max_attempts` — *modified*
- Before: `null`
- After:  `2`

### `spec.call_transfer_protocol.pre_transfer_message` — *modified*
- Before: `"Please hold while I connect you with our team."`
- After:  `"I'm going to connect you with our emergency dispatch now. Please stay on the line."`

### `spec.call_transfer_protocol.routing_order` — *modified*
- Before: `[{"order": 1, "contact": "dispatch coordinator", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "dispatch coordinator", "phone": "303-555-0187", "timeout_seconds": 30}, {"order": 2, "contact": "operations manager", "phone": "303-555-0294", "timeout_seconds": 30}]`

### `spec.call_transfer_protocol.timeout_seconds` — *modified*
- Before: `null`
- After:  `30`

### `spec.fallback_protocol.message` — *modified*
- Before: `"I was unable to reach our team. Someone will call you back."`
- After:  `"I wasn't able to reach our team right now. A technician will call you back within fifteen minutes. Please stay somewhere safe and do not attempt to fix the issue yourself."`

### `spec.integration_constraints` — *modified*
- Before: `["do not create jobs in ServiceTrade automatically"]`
- After:  `["never create jobs in ServiceTrade \u2013 human review required for all new jobs", "do not engage with ServiceTrade job status inquiries \u2013 redirect to business hours"]`

### `spec.key_variables.business_hours_days` — *modified*
- Before: `["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]`
- After:  `["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]`

### `spec.key_variables.business_hours_end` — *modified*
- Before: `"17:00"`
- After:  `"17:30"`

### `spec.key_variables.business_hours_start` — *modified*
- Before: `"08:00"`
- After:  `"07:30"`

### `spec.key_variables.emergency_routing` — *modified*
- Before: `[{"order": 1, "contact": "dispatch coordinator", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "dispatch coordinator", "phone": "303-555-0187", "timeout_seconds": 30}, {"order": 2, "contact": "operations manager", "phone": "303-555-0294", "timeout_seconds": 30}]`

### `spec.key_variables.office_address` — *modified*
- Before: `null`
- After:  `"4820 Havana Street, Denver, Colorado 80239"`

### `spec.questions_or_unknowns` — *modified*
- Before: `["What is the exact on-call dispatch phone number?", "What is the office address?", "What are the exact business hours?", "Is Spanish language support needed?"]`
- After:  `["Spanish language support \u2013 flagged for future enhancement"]`

### `spec.version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

## System Prompt

Prompt **regenerated** from updated memo. See `v2/agent_spec.json`.
