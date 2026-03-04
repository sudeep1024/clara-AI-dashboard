"""
generate_sample_outputs.py
Generates all v1 and v2 outputs WITHOUT requiring an LLM API key.
Uses hardcoded extraction results to demonstrate the full pipeline output structure.
Run this to populate outputs/ for demo/review.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from differ import generate_changelog
from prompt_generator import build_agent_spec
from utils import account_dir, get_logger, save_json, utcnow

log = get_logger("generate_sample_outputs")

# ── Hardcoded extracted memos (simulates LLM extraction from transcripts) ──────
V1_MEMOS = {
"ACC-001": {
  "account_id": "ACC-001",
  "company_name": "BlueSky Fire Protection",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "start": "08:00", "end": "17:00",
    "timezone": "America/Denver", "notes": "Approximate from demo"
  },
  "office_address": None,
  "services_supported": ["fire sprinklers","fire suppression systems","alarm monitoring","annual inspections"],
  "emergency_definition": ["sprinkler head discharging","fire suppression system activation","active fire alarm triggering the system"],
  "emergency_routing_rules": [{"order":1,"contact":"dispatch coordinator","phone":None,"timeout_seconds":None}],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","description"],"notify_method":"none","notify_target":None,"message_to_caller":"We will follow up during business hours."},
  "call_transfer_rules": {"pre_transfer_message":"Please hold while I connect you with our team.","timeout_seconds":None,"max_attempts":None,"transfer_fail_message":"I was unable to reach our team. Someone will call you back."},
  "integration_constraints": ["do not create jobs in ServiceTrade automatically"],
  "after_hours_flow_summary": "Greet caller, determine if emergency (sprinkler/suppression/alarm), attempt transfer to on-call tech, if fail assure callback.",
  "office_hours_flow_summary": "Greet caller, collect name and number, route to appropriate team or take message.",
  "questions_or_unknowns": ["What is the exact on-call dispatch phone number?","What is the office address?","What are the exact business hours?","Is Spanish language support needed?"],
  "notes": "Demo call - directional info only. Routing numbers not yet provided.",
  "_pipeline": "A", "_source_file": "ACC-001_demo.txt", "_extracted_at": utcnow(), "_version": "v1"
},
"ACC-002": {
  "account_id": "ACC-002",
  "company_name": "Apex Alarm & Security",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "start": "09:00", "end": "18:00",
    "timezone": "America/Phoenix", "notes": "Weekends 10:00-15:00"
  },
  "office_address": None,
  "services_supported": ["alarm installation","monitoring contracts","service and repair","system upgrades","camera systems"],
  "emergency_definition": ["verified alarm activation (fire)","verified alarm activation (intrusion)","verified alarm activation (CO)","customer calls in panic about active threat"],
  "emergency_routing_rules": [{"order":1,"contact":"third-party monitoring center","phone":None,"timeout_seconds":None}],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","reason"],"notify_method":"none","notify_target":None,"message_to_caller":"We will follow up next business day."},
  "call_transfer_rules": {"pre_transfer_message":"Let me connect you with our monitoring center.","timeout_seconds":None,"max_attempts":None,"transfer_fail_message":"I was unable to reach our monitoring center. Please call back shortly."},
  "integration_constraints": ["no automated changes to Alarm.com accounts"],
  "after_hours_flow_summary": "Greet, confirm emergency, route to monitoring center, fallback to collect info.",
  "office_hours_flow_summary": "Greet, collect purpose, route or take message.",
  "questions_or_unknowns": ["What is the monitoring center phone number?","What is the office address?","What is the owner's direct number for escalation?"],
  "notes": "Demo call. Monitoring center number and owner cell not yet provided.",
  "_pipeline": "A", "_source_file": "ACC-002_demo.txt", "_extracted_at": utcnow(), "_version": "v1"
},
"ACC-003": {
  "account_id": "ACC-003",
  "company_name": "Pacific HVAC Services",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "start": "07:00", "end": "17:30",
    "timezone": "America/Los_Angeles", "notes": "Closed weekends but accepts emergency calls"
  },
  "office_address": None,
  "services_supported": ["residential HVAC","commercial HVAC","installation","repair","maintenance contracts","emergency service","indoor air quality"],
  "emergency_definition": ["complete system failure in commercial kitchen","no heat in freezing weather","CO detector triggered"],
  "emergency_routing_rules": [{"order":1,"contact":"on-call dispatcher","phone":None,"timeout_seconds":None}],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","description"],"notify_method":"none","notify_target":None,"message_to_caller":"We will follow up during business hours."},
  "call_transfer_rules": {"pre_transfer_message":"Please hold while I connect you with our on-call team.","timeout_seconds":None,"max_attempts":None,"transfer_fail_message":"I was unable to reach our on-call team. A technician will call you back."},
  "integration_constraints": ["do not create jobs in ServiceTitan without human review"],
  "after_hours_flow_summary": "Greet, triage emergency vs non-emergency, transfer for emergency, collect info for non-emergency.",
  "office_hours_flow_summary": "Greet, understand purpose, collect name and number, route or take message.",
  "questions_or_unknowns": ["What is the dispatcher on-call number?","What is the office address?","How many transfer attempts before fallback?"],
  "notes": "Demo call. On-call number and exact routing not yet confirmed.",
  "_pipeline": "A", "_source_file": "ACC-003_demo.txt", "_extracted_at": utcnow(), "_version": "v1"
},
"ACC-004": {
  "account_id": "ACC-004",
  "company_name": "Guardian Electrical Contractors",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "start": "07:00", "end": "17:00",
    "timezone": "America/Chicago", "notes": None
  },
  "office_address": None,
  "services_supported": ["commercial electrical service and repair","panel upgrades","emergency response","code inspections","lighting retrofits","generator hookups"],
  "emergency_definition": ["total power outage at commercial property","exposed or sparking wiring","hot or noisy electrical panel","immediate electrical safety risk"],
  "emergency_routing_rules": [{"order":1,"contact":"on-call lead electrician (rotating)","phone":None,"timeout_seconds":None}],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","description"],"notify_method":"none","notify_target":None,"message_to_caller":"Our team will follow up next business day."},
  "call_transfer_rules": {"pre_transfer_message":"I'm connecting you with our on-call electrician now.","timeout_seconds":None,"max_attempts":None,"transfer_fail_message":"I was unable to reach our on-call team. A technician will call you back."},
  "integration_constraints": ["do not create Jobber jobs automatically without human review"],
  "after_hours_flow_summary": "Greet, confirm emergency, transfer to on-call electrician, fallback if transfer fails.",
  "office_hours_flow_summary": "Greet, collect purpose, route appropriately, take message for non-urgent.",
  "questions_or_unknowns": ["What are the on-call electrician phone numbers?","What is the office address?","Is Spanish language support required?","How many transfer attempts?"],
  "notes": "Demo call. On-call rotation numbers not yet provided. Spanish language mentioned as possible need.",
  "_pipeline": "A", "_source_file": "ACC-004_demo.txt", "_extracted_at": utcnow(), "_version": "v1"
},
"ACC-005": {
  "account_id": "ACC-005",
  "company_name": "Summit Sprinkler & Fire LLC",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "start": "07:00", "end": "16:30",
    "timezone": "America/Chicago", "notes": None
  },
  "office_address": None,
  "services_supported": ["wet pipe sprinkler systems","dry pipe sprinkler systems","backflow prevention","inspection and testing","repair and service","system design"],
  "emergency_definition": ["active water discharge (head activated)","dry pipe system trip","backflow preventer failure with contamination risk"],
  "emergency_routing_rules": [{"order":1,"contact":"on-call technician (shared phone)","phone":None,"timeout_seconds":None}],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","description"],"notify_method":"none","notify_target":None,"message_to_caller":"We will follow up next business day."},
  "call_transfer_rules": {"pre_transfer_message":"Please hold while I connect you with our emergency on-call technician.","timeout_seconds":None,"max_attempts":None,"transfer_fail_message":"I was unable to reach our team. A technician will call you back within fifteen minutes."},
  "integration_constraints": ["never create sprinkler jobs in ServiceTrade","do not create any job automatically without human review"],
  "after_hours_flow_summary": "Greet, determine if active emergency, collect name/number/address, transfer to on-call, fallback if fail.",
  "office_hours_flow_summary": "Greet, understand purpose, collect info, route or take message.",
  "questions_or_unknowns": ["What is the on-call phone number?","What is the office address?","What is the exact transfer timeout?"],
  "notes": "Demo call. Client emphatic about not creating ServiceTrade jobs automatically.",
  "_pipeline": "A", "_source_file": "ACC-005_demo.txt", "_extracted_at": utcnow(), "_version": "v1"
},
}

V2_MEMOS = {
"ACC-001": {
  "account_id": "ACC-001",
  "company_name": "BlueSky Fire Protection",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
    "start": "07:30", "end": "17:30",
    "timezone": "America/Denver", "notes": "Saturday 08:00–12:00 only"
  },
  "office_address": "4820 Havana Street, Denver, Colorado 80239",
  "services_supported": ["fire sprinklers","fire suppression systems","alarm monitoring","annual inspections"],
  "emergency_definition": ["sprinkler head discharging","fire suppression system activation","active fire alarm triggering the system","dry pipe system trip","flooded pipe section"],
  "emergency_routing_rules": [
    {"order":1,"contact":"dispatch coordinator","phone":"303-555-0187","timeout_seconds":30},
    {"order":2,"contact":"operations manager","phone":"303-555-0294","timeout_seconds":30}
  ],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","description"],"notify_method":"email","notify_target":"dispatch@blueskyfireprotection.com","message_to_caller":"We will follow up next business day."},
  "call_transfer_rules": {
    "pre_transfer_message": "I'm going to connect you with our emergency dispatch now. Please stay on the line.",
    "timeout_seconds": 30, "max_attempts": 2,
    "transfer_fail_message": "I wasn't able to reach our team right now. A technician will call you back within fifteen minutes. Please stay somewhere safe and do not attempt to fix the issue yourself."
  },
  "integration_constraints": ["never create jobs in ServiceTrade – human review required for all new jobs","do not engage with ServiceTrade job status inquiries – redirect to business hours"],
  "after_hours_flow_summary": "Greet, state office closed and provide hours, ask purpose, confirm if emergency (5 defined triggers), collect name/number/address, attempt transfer (Sandra 303-555-0187 then Marcus 303-555-0294, 30s each), if fail assure 15-minute callback and confirm callback number.",
  "office_hours_flow_summary": "Greet, ask purpose, collect name and number, route to appropriate team. For emergencies during hours, proceed with emergency transfer protocol.",
  "questions_or_unknowns": ["Spanish language support – flagged for future enhancement"],
  "notes": "Onboarding confirmed. No agent names mentioned to callers. Saturday hours confirmed.",
  "_pipeline": "B", "_source_file": "ACC-001_onboarding.txt", "_onboarding_extracted_at": utcnow(), "_version": "v2", "_previous_version": "v1"
},
"ACC-002": {
  "account_id": "ACC-002",
  "company_name": "Apex Alarm & Security",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "start": "09:00", "end": "18:00",
    "timezone": "America/Phoenix", "notes": "Weekends 10:00–15:00; no DST"
  },
  "office_address": "2201 East Camelback Road, Suite 110, Phoenix, Arizona 85016",
  "services_supported": ["alarm installation","monitoring contracts","service and repair","system upgrades","camera systems"],
  "emergency_definition": ["verified alarm activation (fire)","verified alarm activation (intrusion)","verified alarm activation (CO)","customer reports active threat or panic","customer reports break-in in progress","customer reports smoke or visible fire at monitored property"],
  "emergency_routing_rules": [
    {"order":1,"contact":"third-party monitoring center (24/7)","phone":"602-555-0344","timeout_seconds":45},
    {"order":2,"contact":"owner","phone":"602-555-0771","timeout_seconds":30}
  ],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","reason"],"notify_method":"none","notify_target":None,"message_to_caller":"We will follow up next business day."},
  "call_transfer_rules": {
    "pre_transfer_message": "Let me connect you with our monitoring center right away.",
    "timeout_seconds": 45, "max_attempts": 2,
    "transfer_fail_message": "I wasn't able to reach our monitoring center. If you are in immediate danger, please call 911 now. Otherwise, leave your name and number and we will call you back within thirty minutes."
  },
  "integration_constraints": ["no automated changes to Alarm.com accounts – no write access","never discuss pricing on calls – redirect to business hours"],
  "after_hours_flow_summary": "Greet, ask purpose, confirm emergency status, for emergencies transfer to monitoring center 602-555-0344 (45s) then owner 602-555-0771 (30s), if all fail direct to 911 for life-safety and give 30-min callback assurance.",
  "office_hours_flow_summary": "Greet, collect purpose, collect name and number, route or message. Do not discuss pricing.",
  "questions_or_unknowns": [],
  "notes": "Fully configured at onboarding. Arizona/Phoenix – no DST adjustment needed.",
  "_pipeline": "B", "_source_file": "ACC-002_onboarding.txt", "_onboarding_extracted_at": utcnow(), "_version": "v2", "_previous_version": "v1"
},
"ACC-003": {
  "account_id": "ACC-003",
  "company_name": "Pacific HVAC Services",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "start": "07:00", "end": "17:30",
    "timezone": "America/Los_Angeles", "notes": "Closed weekends but emergency calls accepted"
  },
  "office_address": "8300 Aurora Avenue North, Suite 200, Seattle, Washington 98103",
  "services_supported": ["residential HVAC","commercial HVAC","installation","repair","maintenance contracts","emergency service","indoor air quality"],
  "emergency_definition": ["complete system failure in commercial kitchen","no heat in freezing weather","CO detector triggered","flooding from HVAC drain line or condensate overflow inside building","total cooling failure at data center or server room"],
  "emergency_routing_rules": [
    {"order":1,"contact":"on-call dispatcher","phone":"206-555-0452","timeout_seconds":30},
    {"order":2,"contact":"service manager","phone":"206-555-0819","timeout_seconds":30},
    {"order":3,"contact":"backup technician","phone":"206-555-0631","timeout_seconds":30}
  ],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","property_address","description"],"notify_method":"none","notify_target":None,"message_to_caller":"We will follow up during business hours."},
  "call_transfer_rules": {
    "pre_transfer_message": "Please hold while I connect you with our on-call team.",
    "timeout_seconds": 30, "max_attempts": 3,
    "transfer_fail_message": "I'm sorry, I wasn't able to reach our on-call team directly. Your information has been logged and a technician will call you back within twenty minutes. Is the location safe to remain at?"
  },
  "integration_constraints": ["do not auto-create jobs in ServiceTitan – dispatcher review required"],
  "after_hours_flow_summary": "Greet, ask purpose, determine emergency (5 triggers), collect name/number/property address, attempt 3 transfers (dispatcher 206-555-0452 → Tom 206-555-0819 → Ray 206-555-0631, 30s each), if all fail confirm 20-min callback.",
  "office_hours_flow_summary": "Greet, collect purpose, collect name and number, route or take message. No quotes or pricing on calls.",
  "questions_or_unknowns": ["Spanish language support – flagged for future"],
  "notes": "Three-level emergency routing confirmed. 20-min callback window.",
  "_pipeline": "B", "_source_file": "ACC-003_onboarding.txt", "_onboarding_extracted_at": utcnow(), "_version": "v2", "_previous_version": "v1"
},
"ACC-004": {
  "account_id": "ACC-004",
  "company_name": "Guardian Electrical Contractors",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "start": "07:00", "end": "17:00",
    "timezone": "America/Chicago", "notes": None
  },
  "office_address": "512 West Riverside Drive, Austin, Texas 78704",
  "services_supported": ["commercial electrical service and repair","panel upgrades","emergency response","code inspections","lighting retrofits","generator hookups"],
  "emergency_definition": ["total power outage at commercial property","exposed or sparking wiring","hot or noisy electrical panel","immediate electrical safety risk","electrical fire smell or visible smoke near electrical equipment"],
  "emergency_routing_rules": [
    {"order":1,"contact":"on-call electrician","phone":"512-555-0183","timeout_seconds":30},
    {"order":2,"contact":"backup on-call electrician","phone":"512-555-0247","timeout_seconds":30}
  ],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","description"],"notify_method":"none","notify_target":None,"message_to_caller":"Our team will follow up next business day."},
  "call_transfer_rules": {
    "pre_transfer_message": "I'm connecting you with our on-call electrician now. Please hold.",
    "timeout_seconds": 30, "max_attempts": 2,
    "transfer_fail_message": "I was unable to reach our on-call team. If this is a life-safety emergency, please call 911 immediately. Otherwise, a technician will call you back within fifteen minutes."
  },
  "integration_constraints": ["do not create Jobber jobs automatically – human review required","never reveal on-call technician names to callers – say 'our on-call technician'","never provide price estimates or quotes on calls – redirect to business hours"],
  "after_hours_flow_summary": "Greet, confirm emergency (5 triggers), collect name/number, transfer to on-call 512-555-0183 then 512-555-0247 (30s each), if fail direct to 911 for life-safety risk or give 15-min callback. Spanish language callers supported.",
  "office_hours_flow_summary": "Greet, collect purpose, collect name and number, route or message. No quotes. No on-call names disclosed.",
  "questions_or_unknowns": [],
  "notes": "Spanish language support confirmed. On-call names never disclosed to callers.",
  "_pipeline": "B", "_source_file": "ACC-004_onboarding.txt", "_onboarding_extracted_at": utcnow(), "_version": "v2", "_previous_version": "v1"
},
"ACC-005": {
  "account_id": "ACC-005",
  "company_name": "Summit Sprinkler & Fire LLC",
  "business_hours": {
    "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "start": "07:00", "end": "16:30",
    "timezone": "America/Chicago", "notes": None
  },
  "office_address": "3741 North Kimball Avenue, Chicago, Illinois 60618",
  "services_supported": ["wet pipe sprinkler systems","dry pipe sprinkler systems","backflow prevention","inspection and testing","repair and service","system design"],
  "emergency_definition": ["active water discharge (sprinkler head activated)","dry pipe system trip","backflow preventer failure with contamination risk","fire suppression system activation in commercial kitchen","cracked or burst main riser"],
  "emergency_routing_rules": [
    {"order":1,"contact":"on-call technician (shared rotation phone)","phone":"773-555-0388","timeout_seconds":30},
    {"order":2,"contact":"owner","phone":"773-555-0194","timeout_seconds":30}
  ],
  "non_emergency_routing_rules": {"action":"collect_info","collect_fields":["name","phone","property_address","description"],"notify_method":"none","notify_target":None,"message_to_caller":"We will follow up next business day."},
  "call_transfer_rules": {
    "pre_transfer_message": "Please hold while I connect you with our emergency on-call technician.",
    "timeout_seconds": 30, "max_attempts": 2,
    "transfer_fail_message": "I was unable to reach our team directly. Please remain calm. A technician will call you back within fifteen minutes. In the meantime, if water is actively flowing, locate and shut off the main water supply if it is safe to do so."
  },
  "integration_constraints": ["never create sprinkler jobs in ServiceTrade – this includes all sprinkler and fire suppression job types","inspection scheduling requests may be logged as leads only – not created as jobs","never discuss ServiceTrade job status – redirect to business hours","inspection calls after hours are non-emergency – collect info and follow up next business day only"],
  "after_hours_flow_summary": "Greet, ask purpose, determine emergency (5 triggers), collect name/number/address (partial address accepted), transfer to on-call 773-555-0388 then owner 773-555-0194 (30s each), if fail give 15-min contact assurance with water shutoff guidance if applicable. Inspection calls = non-emergency path only.",
  "office_hours_flow_summary": "Greet, collect purpose, collect info, route or take message. Do not create ServiceTrade jobs.",
  "questions_or_unknowns": [],
  "notes": "Emphatic constraint: no ServiceTrade job creation ever. Partial address ok for emergencies. Inspections = non-emergency after hours.",
  "_pipeline": "B", "_source_file": "ACC-005_onboarding.txt", "_onboarding_extracted_at": utcnow(), "_version": "v2", "_previous_version": "v1"
},
}


def generate_all():
    log.info("Generating all sample outputs (no LLM required)")
    results = []
    for account_id, v1_memo in V1_MEMOS.items():
        log.info("Processing %s...", account_id)
        # v1
        v1_spec = build_agent_spec(v1_memo, "v1")
        out1 = account_dir(account_id, "v1")
        save_json(v1_memo, out1 / "account_memo.json")
        save_json(v1_spec, out1 / "agent_spec.json")

        # v2
        v2_memo = V2_MEMOS[account_id]
        v2_spec = build_agent_spec(v2_memo, "v2")
        out2 = account_dir(account_id, "v2")
        save_json(v2_memo, out2 / "account_memo.json")
        save_json(v2_spec, out2 / "agent_spec.json")

        # changelog
        changelog = generate_changelog(account_id, v1_memo, v2_memo, v1_spec, v2_spec)
        log.info("  ✓ %s — %d changes", account_id, changelog["summary"]["total_changes"])
        results.append({"account_id": account_id, "changes": changelog["summary"]["total_changes"]})

    log.info("\n✓ All outputs generated.")
    for r in results:
        print(f"  {r['account_id']} → {r['changes']} changes")


if __name__ == "__main__":
    generate_all()
