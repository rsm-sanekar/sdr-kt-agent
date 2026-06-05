---
title: Trailhead module catalog (onboarding allow-list)
category: Sales enablement
catalog_version: TH-CATALOG-FY24-Q2
last_reviewed: 2024-10-01
owner: Sales Enablement — Priya Subramanian (Coaching Lead)
audience: SDR onboarding planner, SDR managers, Trail Guides
---

# Trailhead module catalog (TH-CATALOG-FY24-Q2)

This catalog is the **canonical allow-list** of Trailhead modules the SDR onboarding planner is permitted to assign. The `generate-onboarding-plan` skill validates every `module_id` it emits against the IDs below — any `module_id` not present here triggers `review_required=true` on the run envelope.

Curation lives with Sales Enablement (Priya Subramanian). The catalog is refreshed quarterly; module URLs that 404 are pruned at the same cadence.

## How the planner uses this catalog

1. The catalog is RAG-retrieved and pasted into the planner's system prompt under "ALLOW-LIST" before the LLM call.
2. The LLM is instructed to only emit `module_id` values from the allow-list and to attach a one-sentence rationale to each.
3. After the LLM responds, the skill parses every `module_id` out of the catalog (regex over the table below) and rejects any plan that contains an unknown id by flagging it for human review.

## Modules

| Module ID | Title | Vertical | Level | URL |
|---|---|---|---|---|
| TRAIL-CRM-101 | Salesforce CRM Basics | any | entry | https://trailhead.salesforce.example/learn/modules/crm-basics |
| TRAIL-CRM-201 | Advanced CRM Navigation | any | mid | https://trailhead.salesforce.example/learn/modules/crm-navigation-201 |
| TRAIL-OUT-101 | Outreach Foundations | any | entry | https://trailhead.salesforce.example/learn/modules/outreach-foundations |
| TRAIL-DISC-101 | Discovery Calls I | any | entry | https://trailhead.salesforce.example/learn/modules/discovery-calls-1 |
| TRAIL-DISC-201 | Discovery Calls II | any | mid | https://trailhead.salesforce.example/learn/modules/discovery-calls-2 |
| TRAIL-DISC-301 | Strategic Discovery | any | senior | https://trailhead.salesforce.example/learn/modules/strategic-discovery |
| TRAIL-PROS-101 | Prospecting 101 | any | entry | https://trailhead.salesforce.example/learn/modules/prospecting-101 |
| TRAIL-PROS-201 | Prospecting 201 | any | mid | https://trailhead.salesforce.example/learn/modules/prospecting-201 |
| TRAIL-COLD-101 | Cold Call Mechanics | any | entry | https://trailhead.salesforce.example/learn/modules/cold-call-mechanics |
| TRAIL-OBJ-101 | Objection Handling Patterns | any | entry | https://trailhead.salesforce.example/learn/modules/objection-handling-101 |
| TRAIL-OBJ-201 | Advanced Objection Handling | any | mid | https://trailhead.salesforce.example/learn/modules/objection-handling-201 |
| TRAIL-MULTI-301 | Multi-Threading Accounts | any | senior | https://trailhead.salesforce.example/learn/modules/multi-threading |
| TRAIL-MEDDIC-301 | MEDDIC Deal Qualification | any | senior | https://trailhead.salesforce.example/learn/modules/meddic |
| TRAIL-COMP-301 | Competitive Landscape Briefing | any | senior | https://trailhead.salesforce.example/learn/modules/competitive-landscape |
| TRAIL-WIN-301 | Win-Room Participation | any | senior | https://trailhead.salesforce.example/learn/modules/win-room |
| TRAIL-CRM-HYG-101 | Post-Call CRM Hygiene | any | entry | https://trailhead.salesforce.example/learn/modules/crm-hygiene |
| TRAIL-VERT-HC-101 | HIPAA-Aware Selling | healthcare | entry | https://trailhead.salesforce.example/learn/modules/hipaa-aware-selling |
| TRAIL-VERT-HC-201 | Healthcare Buyer Personas (Payer vs Provider) | healthcare | mid | https://trailhead.salesforce.example/learn/modules/healthcare-personas |
| TRAIL-VERT-HC-301 | Veeva and Provider Workflows | healthcare | senior | https://trailhead.salesforce.example/learn/modules/veeva-provider |
| TRAIL-VERT-FT-101 | Fintech Regulatory Landscape | fintech | entry | https://trailhead.salesforce.example/learn/modules/fintech-regulatory |
| TRAIL-VERT-FT-201 | Core Banking Integration Patterns | fintech | mid | https://trailhead.salesforce.example/learn/modules/core-banking |
| TRAIL-VERT-SAAS-101 | SaaS Pricing and Procurement | SaaS | entry | https://trailhead.salesforce.example/learn/modules/saas-pricing |
| TRAIL-VERT-RET-101 | Retail Buying Cycles | retail | entry | https://trailhead.salesforce.example/learn/modules/retail-buying-cycles |
| TRAIL-TERR-AMER-101 | AMER Outreach Cadence | any | entry | https://trailhead.salesforce.example/learn/modules/amer-cadence |
| TRAIL-TERR-EMEA-101 | EMEA Outreach + GDPR Awareness | any | entry | https://trailhead.salesforce.example/learn/modules/emea-gdpr |
| TRAIL-TERR-APAC-101 | APAC Regional Buying Customs | any | entry | https://trailhead.salesforce.example/learn/modules/apac-customs |

## Module-id format

Every module id starts with the prefix `TRAIL-` followed by a domain tag (`CRM`, `DISC`, `VERT-HC`, etc.) and a level suffix (`-101`, `-201`, `-301`). The planner uses the level suffix as a soft signal of module depth, but the binding constraint is allow-list membership: any `module_id` not in this table is rejected.
