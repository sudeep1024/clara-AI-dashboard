# Changelog: ACC-002

**Generated:** 2026-03-04T05:28:28.979083+00:00
**Total changes:** 30

---

## Memo Changes (19)

### `memo._extracted_at` — *removed*
- Removed: `"2026-03-04T05:28:28.971071+00:00"`

### `memo._onboarding_extracted_at` — *added*
- Added: `"2026-03-04T05:28:28.971096+00:00"`

### `memo._pipeline` — *modified*
- Before: `"A"`
- After:  `"B"`

### `memo._previous_version` — *added*
- Added: `"v1"`

### `memo._source_file` — *modified*
- Before: `"ACC-002_demo.txt"`
- After:  `"ACC-002_onboarding.txt"`

### `memo._version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

### `memo.after_hours_flow_summary` — *modified*
- Before: `"Greet, confirm emergency, route to monitoring center, fallback to collect info."`
- After:  `"Greet, ask purpose, confirm emergency status, for emergencies transfer to monitoring center 602-555-0344 (45s) then owner 602-555-0771 (30s), if all fail direct to 911 for life-safety and give 30-min callback assurance."`

### `memo.business_hours.notes` — *modified*
- Before: `"Weekends 10:00-15:00"`
- After:  `"Weekends 10:00\u201315:00; no DST"`

### `memo.call_transfer_rules.max_attempts` — *modified*
- Before: `null`
- After:  `2`

### `memo.call_transfer_rules.pre_transfer_message` — *modified*
- Before: `"Let me connect you with our monitoring center."`
- After:  `"Let me connect you with our monitoring center right away."`

### `memo.call_transfer_rules.timeout_seconds` — *modified*
- Before: `null`
- After:  `45`

### `memo.call_transfer_rules.transfer_fail_message` — *modified*
- Before: `"I was unable to reach our monitoring center. Please call back shortly."`
- After:  `"I wasn't able to reach our monitoring center. If you are in immediate danger, please call 911 now. Otherwise, leave your name and number and we will call you back within thirty minutes."`

### `memo.emergency_definition` — *modified*
- Before: `["verified alarm activation (fire)", "verified alarm activation (intrusion)", "verified alarm activation (CO)", "customer calls in panic about active threat"]`
- After:  `["verified alarm activation (fire)", "verified alarm activation (intrusion)", "verified alarm activation (CO)", "customer reports active threat or panic", "customer reports break-in in progress", "customer reports smoke or visible fire at monitored property"]`

### `memo.emergency_routing_rules` — *modified*
- Before: `[{"order": 1, "contact": "third-party monitoring center", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "third-party monitoring center (24/7)", "phone": "602-555-0344", "timeout_seconds": 45}, {"order": 2, "contact": "owner", "phone": "602-555-0771", "timeout_seconds": 30}]`

### `memo.integration_constraints` — *modified*
- Before: `["no automated changes to Alarm.com accounts"]`
- After:  `["no automated changes to Alarm.com accounts \u2013 no write access", "never discuss pricing on calls \u2013 redirect to business hours"]`

### `memo.notes` — *modified*
- Before: `"Demo call. Monitoring center number and owner cell not yet provided."`
- After:  `"Fully configured at onboarding. Arizona/Phoenix \u2013 no DST adjustment needed."`

### `memo.office_address` — *modified*
- Before: `null`
- After:  `"2201 East Camelback Road, Suite 110, Phoenix, Arizona 85016"`

### `memo.office_hours_flow_summary` — *modified*
- Before: `"Greet, collect purpose, route or take message."`
- After:  `"Greet, collect purpose, collect name and number, route or message. Do not discuss pricing."`

### `memo.questions_or_unknowns` — *modified*
- Before: `["What is the monitoring center phone number?", "What is the office address?", "What is the owner's direct number for escalation?"]`
- After:  `[]`

## Spec Changes (10)

### `spec.call_transfer_protocol.max_attempts` — *modified*
- Before: `null`
- After:  `2`

### `spec.call_transfer_protocol.pre_transfer_message` — *modified*
- Before: `"Let me connect you with our monitoring center."`
- After:  `"Let me connect you with our monitoring center right away."`

### `spec.call_transfer_protocol.routing_order` — *modified*
- Before: `[{"order": 1, "contact": "third-party monitoring center", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "third-party monitoring center (24/7)", "phone": "602-555-0344", "timeout_seconds": 45}, {"order": 2, "contact": "owner", "phone": "602-555-0771", "timeout_seconds": 30}]`

### `spec.call_transfer_protocol.timeout_seconds` — *modified*
- Before: `null`
- After:  `45`

### `spec.fallback_protocol.message` — *modified*
- Before: `"I was unable to reach our monitoring center. Please call back shortly."`
- After:  `"I wasn't able to reach our monitoring center. If you are in immediate danger, please call 911 now. Otherwise, leave your name and number and we will call you back within thirty minutes."`

### `spec.integration_constraints` — *modified*
- Before: `["no automated changes to Alarm.com accounts"]`
- After:  `["no automated changes to Alarm.com accounts \u2013 no write access", "never discuss pricing on calls \u2013 redirect to business hours"]`

### `spec.key_variables.emergency_routing` — *modified*
- Before: `[{"order": 1, "contact": "third-party monitoring center", "phone": null, "timeout_seconds": null}]`
- After:  `[{"order": 1, "contact": "third-party monitoring center (24/7)", "phone": "602-555-0344", "timeout_seconds": 45}, {"order": 2, "contact": "owner", "phone": "602-555-0771", "timeout_seconds": 30}]`

### `spec.key_variables.office_address` — *modified*
- Before: `null`
- After:  `"2201 East Camelback Road, Suite 110, Phoenix, Arizona 85016"`

### `spec.questions_or_unknowns` — *modified*
- Before: `["What is the monitoring center phone number?", "What is the office address?", "What is the owner's direct number for escalation?"]`
- After:  `[]`

### `spec.version` — *modified*
- Before: `"v1"`
- After:  `"v2"`

## System Prompt

Prompt **regenerated** from updated memo. See `v2/agent_spec.json`.
