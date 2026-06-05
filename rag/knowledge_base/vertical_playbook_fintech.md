---
title: Fintech vertical selling playbook
category: Vertical playbook
codename: Project Ledger
last_reviewed: 2024-09-22
owner: Industry Marketing — Hiroshi Tanaka (Financial Services GTM Lead)
audience: SDRs and AEs working fintech, banking, and capital-markets accounts
---

# Fintech playbook — "Project Ledger"

Internal codename for our financial-services GTM is **Project Ledger**. The motion covers retail and commercial banking, lending fintechs, payments processors, and capital markets. This document equips SDRs to qualify a fintech opportunity through to discovery.

## SOC 2 talking points

Compliance is table stakes — prospects ask for SOC 2 reports during the first conversation, sometimes before agreeing to a follow-up call. SDRs may state, without legal review:

- Salesforce maintains current **SOC 2 Type II** reports for Sales Cloud, Service Cloud, and Financial Services Cloud (FSC), refreshed annually. The most recent report cycle closed **August 2024**.
- Reports are available under MNDA via the Compliance Portal (request through the AE).
- Hyperforce additionally carries ISO 27001, ISO 27017, ISO 27018, and PCI-DSS Level 1 attestations.
- Customer data residency can be pinned to specific Hyperforce regions; the current FedRAMP High region is **GovCloud Plus** (US only).

Do not commit to specific audit dates, scope inclusions, or compensating controls beyond what is in the published trust packet.

## Banking-platform integration patterns

Three integration patterns are sanctioned for SDR mentions; deeper architectural conversations escalate to the FSC SE team.

1. **Core-banking sync via MuleSoft** — pre-built connectors for FIS, Fiserv, Jack Henry, and Temenos. Reference architecture diagram: internal doc `FSC-INTEG-007`.
2. **Real-time ledger events via Pub/Sub API** — used by lending fintechs to push loan-status changes into Salesforce in under 200ms.
3. **Open Banking via the FSC Open Banking Adapter** — UK and EU PSD2 flows, AISP and PISP modes both supported.

## Regulatory considerations

Fintech buyers frequently flag the same four regimes. Approved SDR-level acknowledgements:

- **GLBA (US):** FSC supports data-handling controls aligned with GLBA safeguards.
- **PSD2 (EU/UK):** Open Banking Adapter is PSD2-aware.
- **Dodd-Frank / SR 11-7 (model risk):** AI features can be configured for model-governance documentation.
- **MiFID II (EU):** Call recording and record-retention integrations available.

Anything beyond acknowledgement — particularly opinions on whether the prospect *is* covered by a given regime — must be routed to **Hiroshi Tanaka** or the FSC compliance specialist.
