# Cast of characters (naming reference — NOT a RAG document)

This file keeps every name in the demo distinct and intentional: one person =
one name = one role. It is deliberately stored under `data/raw/` (not
`rag/knowledge_base/`) so it is never indexed into the retriever. Update it
whenever you add or rename a profile, persona, mentor, or document owner.

**Rule:** no full name is reused across roles. First-name repeats are allowed
only when surnames clearly differ (e.g. Priya Sharma vs Priya Subramanian).

## SDR trainees — certified cohort (in both `sdr_profiles.csv` and `sdr_records/`)

| Name | Hire id | SDR id | Territory | Vertical | Exp | Cert result |
|---|---|---|---|---|---|---|
| Priya Sharma | HIRE-001 | SDR-001 | EMEA | healthcare | entry | BORDERLINE |
| Marcus Chen | HIRE-002 | SDR-002 | AMER-West | fintech | mid | PASS |
| Aisha Patel | HIRE-011 | SDR-003 | AMER-East | SaaS | entry | FAIL |
| Diego Rodriguez | HIRE-012 | SDR-004 | EMEA | retail | entry | BORDERLINE |
| Sarah Kim | HIRE-013 | SDR-005 | AMER-West | healthcare | mid | PASS |
| Liam O'Brien | HIRE-004 | SDR-006 | EMEA | fintech | senior | PASS |
| Yuki Tanaka | HIRE-014 | SDR-007 | AMER-East | manufacturing | mid | PASS |

## SDR trainees — pipeline only (hire profile, not yet certified)

| Name | Hire id | Territory | Vertical | Exp |
|---|---|---|---|---|
| Sofia Ramirez | HIRE-003 | AMER-East | fintech | senior |
| Amara Okonkwo | HIRE-005 | APAC | retail | mid |
| Daniel Cho | HIRE-006 | AMER-West | healthcare | senior |
| Hannah Weiss | HIRE-007 | EMEA | fintech | mid |
| Raj Sundaram | HIRE-008 | APAC | SaaS | entry |
| Emma Larsson | HIRE-009 | AMER-East | retail | senior |
| Tomas Novak | HIRE-010 | APAC | fintech | mid |

## Mentors / Account Executives (`ae_profiles.csv`)

Olivia Hartmann (AE-001), Brandon Walsh (AE-002), Natalie Reyes (AE-003),
Sean Murphy (AE-004), Mei Lin Tan (AE-005), Carlos Mendoza (AE-006),
Lukas Becker (AE-007), Hiroshi Nakamura (AE-008), Rebecca Goldstein (AE-009),
Anjali Sharma (AE-010), Fiona MacLeod (AE-011), Tyler Jackson (AE-012),
Diego Fernandez (AE-013), Wei Zhang (AE-014), Charlotte Dubois (AE-015).

## Cold-call prospect personas (`sim_personas.json`)

| Name | Role | Company | Vertical |
|---|---|---|---|
| Gregory Hale | CFO | NorthLake SaaS | SaaS |
| Dr. Lena Hassan | Chief Medical Officer | Meridian Health | healthcare |
| Naomi Park | Director of IT | Apex Capital | fintech |
| Sam Rivera | VP of Operations | Pinewood Retail | retail |
| Hank Mueller | VP of Manufacturing Operations | Cedarcrest Industrial | manufacturing |
| Robin Lee | Executive Assistant | (gatekeeper) | any |

## Knowledge-base document owners (`rag/knowledge_base/*`)

Trevor Ellison (Onboarding Operations), Kenji Watanabe (FinTech GTM Lead),
Priya Subramanian (Coaching Lead), Janelle Foster (SDR Comp Lead),
Devon Park (Mentor Program Lead), Linh Truong (IT Access Lead),
Dr. Anita Bhatt (Healthcare GTM Lead), Maya Reyes (People Ops),
Sasha Lindgren (Sales Counsel), Ravi Anand (Director of Sales Ops).

## Resolved collisions (history)

- **Marcus Chen** was previously also a prospect persona and a doc owner →
  persona renamed **Gregory Hale**, doc owner renamed **Trevor Ellison**.
  Marcus Chen now refers only to the SDR trainee (HIRE-002 / SDR-002).
- **Hiroshi Tanaka** was both a mentor (AE-008) and the fintech-playbook owner
  → mentor renamed **Hiroshi Nakamura**, owner renamed **Kenji Watanabe**.
  Tanaka now refers only to the SDR trainee Yuki Tanaka (SDR-007).
- HIRE↔SDR name mismatches resolved: Priya Patel→**Priya Sharma**;
  Aisha Okonkwo (hire)→**Amara Okonkwo** to free "Aisha Patel" for SDR-003;
  Daniel Kim→**Daniel Cho** to free "Kim" for Sarah Kim (SDR-005).
