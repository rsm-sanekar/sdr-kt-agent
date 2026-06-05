---
title: Internal sales territory definitions
category: Sales operations
effective_date: 2024-01-01
last_reviewed: 2024-07-15
owner: Sales Operations (Ravi Anand, Director of Sales Ops)
audience: SDRs, AEs, RevOps, Comp
---

# Internal sales territory definitions

This document defines how Salesforce splits the four global sales territories used by the SDR and AE org. Definitions are effective **January 2024** and are referenced by the comp plan, lead-routing rules, and the Trail Guide pairing scorer. Questions: **Ravi Anand, Director of Sales Operations**.

## The four territories

### AMER-West
United States: Alaska, Arizona, California, Colorado, Hawaii, Idaho, Montana, Nevada, New Mexico, Oregon, Utah, Washington, Wyoming. Canada: British Columbia, Alberta, Yukon. Mexico (national). Headquartered out of San Francisco; SDR pod leads from Indianapolis cover overflow.

### AMER-East
United States: all states east of and including the Central time zone except those listed in AMER-West. Canada: Ontario, Quebec, Nova Scotia, New Brunswick, Newfoundland & Labrador, PEI, Manitoba, Saskatchewan. **Brazil is in AMER-East** for both lead routing and comp purposes (this is the most-asked edge case). Other LATAM countries are unassigned and routed through partner channel.

### EMEA
Europe (all EU and EEA states, UK, Switzerland, Norway, Iceland), Middle East, Africa. **The UAE is in EMEA**, *not* APAC — a common error when reading region by longitude. Israel is in EMEA. Turkey is in EMEA. South Africa is the only sub-Saharan country with a dedicated SDR seat.

### APAC
Australia, New Zealand, Japan, South Korea, Singapore, Malaysia, Thailand, Vietnam, Indonesia, Philippines, Hong Kong, Taiwan. **India is in APAC** and has its own dedicated pod in Bengaluru — do not route Indian leads through EMEA. Mainland China is partner-routed and not directly served by the SDR org.

## Edge cases worth memorizing

These come up enough that the lead-routing engine warns when a rep types them into a manual reassignment:

- **Brazil → AMER-East** (not LATAM-unassigned)
- **UAE → EMEA** (not APAC)
- **India → APAC** (not EMEA)
- **Mexico → AMER-West** (not LATAM-unassigned)
- **South Africa → EMEA** (the only sub-Saharan default)
- **Israel → EMEA**

Rerouting an account outside these defaults requires an exception ticket to RevOps and 48 hours' notice before the next comp cycle.
