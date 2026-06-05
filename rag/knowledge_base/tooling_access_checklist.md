---
title: New-SDR tooling access checklist
category: IT runbook
ticket_template: ACCESS-2024-NEWSDR
last_reviewed: 2024-09-15
owner: IT Service Desk — Linh Truong (Endpoint & Access Lead)
audience: IT Service Desk, hiring managers, new SDR hires
---

# Tooling access checklist (ticket ACCESS-2024-NEWSDR)

Every new SDR hire kicks off a ticket from the **ACCESS-2024-NEWSDR** template the moment the offer is accepted. The template defines the provisioning order, SLA, and approval gate for each tool. Hires whose first-day tooling is incomplete are escalated to **Linh Truong** by 11:00 AM local time on Day 1.

## Day-1 access (provisioned before the hire's first login)

These four tools must be live on Day 1. The Service Desk runs a 24-hour pre-start audit:

- **Salesforce CRM** — production org seat with the `SDR Standard` profile. Sandbox access is requested separately.
- **Outreach** — full seat, default cadence library imported. Personal sequences must be reviewed by the Trail Guide before being sent.
- **Slack** — added to `#sdr-global`, the regional pod channel, and `#trail-guides-cohort-2024`.
- **Google Workspace** — calendar and meet, mailbox provisioned with the SDR signature template.

## Day-3 access

- **Gong** — recording and review seat. Auto-recording is enabled for all outbound dials by default. New hires *cannot* opt their own line out — that requires a Legal exception.

## Week-2 access

- **LinkedIn Sales Navigator** — Advanced seat, including TeamLink. License pool is regional; if the pool is exhausted, the hire is placed in queue and the manager is notified.

## After manager approval

- **ZoomInfo** — requires written approval from the hire's SDR manager because seat cost is allocated to the manager's discretionary budget. Provisioning happens within 2 business days of approval. Justification of business need is filed in the ticket comment.

## Deprovisioning

If a hire does not start (offer rescinded or candidate withdraws), the Service Desk deprovisions all access within 4 hours of People Ops notification. If a hire exits within the 90-day window, the same SLA applies but the Trail Guide must hand the in-flight opportunities to the SDR manager within 24 hours.

## Common Day-1 issues

The single most common ticket-reopen reason is the new hire's laptop arriving without the Outreach desktop integration preinstalled. The fix is to push image `MAC-SDR-2024-08` from the MDM console — Linh's team owns this.
