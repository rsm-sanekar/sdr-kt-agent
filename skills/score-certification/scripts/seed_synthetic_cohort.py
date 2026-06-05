"""Seed the demo cohort under ``data/sdr_records/``.

Idempotent — re-running this script skips any SDR record that already exists.
Produces 7 SDRs with realistic journey data so the certification roster
demo loads instantly without LLM calls:

- 4 PASS (SDR-002, 005, 006, 007)
- 2 BORDERLINE (SDR-001, 004)
- 1 FAIL (SDR-003)

For each SDR, writes:
- ``<sdr_id>.json`` — index record with events
- ``<sdr_id>/call-1-transcript.md`` (and call-2 for some) — simulation transcript
- ``<sdr_id>/certification-exam.md`` — 5 Q&A pairs answering the canonical questions
- ``<sdr_id>/coaching-note-1.md`` — short manager feedback (some SDRs only)
- ``<sdr_id>/gap_analysis.json`` — pre-baked envelope shaped like score-certification's output
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SDR_RECORDS_DIR = REPO_ROOT / "data" / "sdr_records"

# ---------------------------------------------------------------------------
# Per-SDR seed data
# ---------------------------------------------------------------------------

COHORT_LABEL = "Spring 2026"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Transcript templates — keyed by archetype. Each is a realistic short cold-call
# excerpt that lines up with the SDR's expected verdict.
TRANSCRIPT_PASS_STRONG = """SDR: Hi {prospect_name}, thanks for the few minutes. I'm calling because three other {vertical} ops leaders we work with were spending 18-22 hours a week on manual pipeline hygiene before they moved to Sales Cloud. Does that pattern sound familiar at your scale, or is your team in a different place?

Prospect: Honestly, my reps spend more time updating CRM than selling. It's a problem.

SDR: That's the exact pain we hear. Before I assume Sales Cloud is right, can you walk me through where the data actually lives today — is it in Salesforce, in spreadsheets, or somewhere in between?

Prospect: Mostly in Salesforce, but the reps don't trust the forecast numbers, so we rebuild them in Excel weekly.

SDR: Got it — so the friction isn't capture, it's confidence in what's in the system. A few of your peers have used Sales Cloud's revenue intelligence layer to close that trust gap; what would actually have to be true for your forecast to be the one number everyone runs the business on?

Prospect: Clean stage definitions, owner accountability, and something that flags stalled deals before my reviews on Friday.

SDR: All three are addressable inside Sales Cloud. The piece I'd want to dig into with you is who else weighs in when you're changing the forecast rhythm — is that you, or do you have a finance partner and a RevOps lead in that decision?

Prospect: Finance VP and my RevOps lead. We'd need both to sign off.

SDR: Helpful — I'd want to bring those two into the conversation before we propose anything specific. Would Thursday at 11 work for a 30-minute scoping call with you and the RevOps lead?

Prospect: Yes, Thursday at 11 works.

SDR: Done. I'll send a calendar hold and a one-pager covering the three pieces you mentioned — stage definitions, stalled-deal flags, and the forecast rhythm. Anything you want me to add?

Prospect: Maybe how this integrates with our finance system.

SDR: Adding that to the deck. Talk Thursday.
"""

TRANSCRIPT_BORDERLINE_DEFENSIVE = """SDR: Hi {prospect_name}, do you have two minutes? I think Salesforce could help your team.

Prospect: We already have a CRM and honestly we're not looking right now.

SDR: I hear that a lot, but Sales Cloud is different from what you probably have today.

Prospect: I'm not sure what's different.

SDR: It has AI features, automation, and integrates with everything.

Prospect: We have AI features in our current CRM.

SDR: But Salesforce's AI is more advanced. Companies see big productivity gains.

Prospect: How big?

SDR: Some report 30% productivity improvement.

Prospect: That sounds inflated. What's the source?

SDR: It's a number we use internally — I can dig into it.

Prospect: Right.

SDR: Look, what if I send you a one-pager and you can take a look?

Prospect: Sure, send it.

SDR: Great. What's a good time to follow up next week?

Prospect: Just email me, I'll get back to you when I have time.

SDR: Okay, thanks.
"""

TRANSCRIPT_FAIL_FEATURE_DUMP = """SDR: Hi {prospect_name}, I'm calling about Salesforce. Sales Cloud has incredible features.

Prospect: Such as?

SDR: It has case management, customer service automation, knowledge base, ticket routing, chatbots — basically everything you'd want for handling customer issues.

Prospect: Wait, isn't that Service Cloud?

SDR: Sales Cloud and Service Cloud are basically the same thing — they all run on the Salesforce platform.

Prospect: Hmm, I thought Sales Cloud was for pipeline and Service Cloud was for support cases.

SDR: They overlap a lot. The point is Salesforce can do whatever you need. We have customers who've doubled their revenue using it.

Prospect: Doubled? Across what timeframe?

SDR: It varies, but the ROI is huge.

Prospect: Can you point me to a published case study?

SDR: I'll have to get back to you on that. But I can also tell you about Marketing Cloud — that's our newest product, just launched last year.

Prospect: Marketing Cloud has been around for over a decade.

SDR: Maybe I'm thinking of a different one. Look, what I want is to set up a demo so you can see for yourself.

Prospect: I don't think Salesforce is the right fit for us. Thanks for the call.
"""

TRANSCRIPT_BORDERLINE_MEDDIC_PARTIAL = """SDR: Hi {prospect_name}, three retail ops teams I spoke to this quarter were losing 12 hours a week reconciling store-level orders against the CRM. Is that a problem you're seeing at your scale?

Prospect: Yes, and it's getting worse as we add stores.

SDR: That's the pattern. Can I ask — when you say it's getting worse, what does that cost you in real terms? Late orders? Returns? Lost deals?

Prospect: Mostly delayed reordering and we miss seasonal windows.

SDR: That's a clear quantifiable impact. How are you currently solving for it?

Prospect: Manual spreadsheets and one analyst's full-time job.

SDR: Got it. If we showed you a way to automate that reconciliation inside Sales Cloud, what does the success metric look like? Hours saved? Faster reordering? Both?

Prospect: Both, but hours saved is what my CFO would track.

SDR: Helpful — so if I'm bringing this to you and your CFO, who else is in the decision? Procurement? Your IT lead?

Prospect: My team and I would scope it. Procurement is just paperwork.

SDR: And budget?

Prospect: I have budget authority up to a certain level.

SDR: That's useful context. Would you be open to a 30-minute working session next week where I bring our retail solutions lead and we map your specific reconciliation flow to what Sales Cloud automates out of the box?

Prospect: Yes, schedule it for Wednesday.

SDR: Done. I'll send a calendar hold.
"""

TRANSCRIPT_PASS_DISCOVERY = """SDR: Hi {prospect_name}, before I assume anything about what you need, can I ask what your team is focused on this quarter?

Prospect: We're trying to shorten our sales cycle in the provider segment. It's running 14 months and that's killing us.

SDR: 14 months is long. What do you see as the biggest contributor — internal review processes, vendor negotiation, or something earlier in the funnel?

Prospect: Honestly, qualification. We waste months on deals that aren't real.

SDR: Tell me more — what does an unqualified deal look like, in retrospect?

Prospect: No budget, no executive sponsor, the champion goes silent.

SDR: That's MEDDIC, basically — economic buyer and champion missing. Are you using a structured framework today?

Prospect: Loosely. The reps are inconsistent.

SDR: Got it. What would have to be true for you to feel confident every deal in the forecast has an EB identified before it advances stage?

Prospect: A system that won't let them advance without it.

SDR: That's enforceable inside Sales Cloud. Who else weighs in on changing the qualification process — your VP, RevOps?

Prospect: My VP and our RevOps director.

SDR: Would you bring them to a 45-minute working session next Thursday where I walk through how Sales Cloud enforces MEDDIC at stage transitions? I'll prep three real anonymized examples.

Prospect: Yes. Send the invite.
"""

TRANSCRIPT_PASS_VALUE_MESSAGING = """SDR: Hi {prospect_name}, I won't pitch — I want to understand whether what we do is relevant. What's the financial pressure on your team this year?

Prospect: We're being asked to grow pipeline 20% without adding headcount.

SDR: 20% with the same team. How are you thinking about getting there?

Prospect: Better targeting, better tooling. I'm honestly not sure.

SDR: Fair. Two of your FinTech peers I worked with last quarter were stuck on the same math. Both used Sales Cloud + Data Cloud to enrich existing accounts so reps spent 4x more time on accounts with actual buying signal. One added $8M in pipeline in two quarters with the same headcount.

Prospect: That's specific. What did they have to do?

SDR: The unlock was their RevOps team mapping signal data — funding rounds, exec hires, tech-stack changes — back to the account ownership in Sales Cloud. Took about 8 weeks to stand up. Is that work your team has the capacity for, or is that a blocker?

Prospect: My RevOps lead would love it but we'd need to scope the lift.

SDR: Right call. Want to put 30 minutes on the calendar with him and me, and I'll bring the actual implementation timeline those two FinTech teams used? You'd leave knowing if this is feasible for your team or not.

Prospect: Yes — Wednesday at 2 works.
"""

TRANSCRIPT_PASS_PRODUCT_FLUENCY = """SDR: Hi {prospect_name}, calling because three manufacturing CFOs I've worked with this year were trying to consolidate their customer data across plant-level ERPs and a separate CRM. Is that a friction point for you?

Prospect: It's the friction point. We have eight ERP instances.

SDR: Eight is a lot. What hurts most — quote accuracy across plants, or service handoffs when an order arrives?

Prospect: Quote accuracy. Reps don't know what's actually available at which plant.

SDR: That's a Data Cloud problem more than a Sales Cloud problem — you'd want a single source of truth that pulls plant-level inventory into the rep's quote workflow. Service Cloud isn't relevant here unless you've got a post-sale case-routing problem too.

Prospect: We have that downstream, but quote accuracy is the immediate pain.

SDR: Got it. Data Cloud as the foundation, Sales Cloud surfacing the consolidated view in the quote builder, Service Cloud later. What does the decision process look like for something at this scope — IT, procurement, line of business?

Prospect: All three, and my CFO signs off.

SDR: Would it help if I brought our manufacturing solution architect to a 45-minute call where we map your plant ERPs to a Data Cloud target architecture? You'd see whether the lift is realistic before any of those decision makers are in the room.

Prospect: Yes, set it up.
"""

# Exam answer templates ----------------------------------------------------

EXAM_PASS_PRODUCT = """### Q1 — Product knowledge accuracy

The five core Salesforce clouds and their business outcomes:

- **Sales Cloud** — pipeline and opportunity management. Reps and managers run their forecast, accounts, and sales process here. Outcome: predictable revenue and shorter time-to-close.
- **Service Cloud** — case management and customer service. Handles post-sale support tickets, knowledge base, and customer self-service. Outcome: faster case resolution and lower support cost per case.
- **Marketing Cloud** — multi-channel marketing automation, journeys, email/SMS. Outcome: higher engagement and qualified pipeline created by marketing.
- **Data Cloud** — the underlying customer data platform that unifies records across the other clouds and external systems. Outcome: one trusted view of each customer that every team operates from.
- **Agentforce** — the AI layer that runs on top, automating routine work in any of the above clouds. Outcome: time saved on repetitive tasks and faster response times.

Sales Cloud and Service Cloud are distinct products with different schemas — Sales Cloud is built around the Opportunity object, Service Cloud around the Case object. I would not blur them.
"""

EXAM_PASS_OBJECTION = """### Q2 — Objection handling (Defuse, Discover, Deliver)

On a price objection, I would not lead with a discount or a defense of the price. Three steps:

**Defuse** — Acknowledge the concern and the emotion. "That's a fair question — budget conversations are always tough this time of year. Thank you for raising it directly."

**Discover** — Ask an open-ended question to surface what's actually behind the objection. "Can you walk me through what's driving the budget concern — is it the absolute number, the timing relative to your fiscal year, or the comparison against another vendor?" The first objection is usually surface; the real concern sits underneath.

**Deliver** — Once I know the real driver, I reframe to value. If it's timing, I bring in the cost of waiting (lost productivity over the deferral window). If it's a vendor comparison, I quantify the differentiator. If it's the absolute number, I tie the investment to a quantified business outcome they already mentioned earlier in discovery.

I would not give a discount on the first call.
"""

EXAM_PASS_MEDDIC = """### Q3 — MEDDIC framework application

Captured in this scenario:
- **C — Champion**: yes, the Director of Operations is engaged across three calls.
- **I — Identify Pain**: implied but not stated. I would push to quantify the pain before advancing.
- **D — Decision Criteria**: partial. I have informal signal but no documented requirements list.

Missing:
- **M — Metrics**: I have not heard a quantified business outcome the prospect would attach to this purchase. Without this the deal has no ROI story.
- **E — Economic Buyer**: critical gap. The Director of Operations is not the person who signs off on this size of spend. I need to identify and meet the VP or the actual budget owner.
- **D — Decision Process**: I have no timeline, no list of approvals, no map of who else is involved.

**Verdict**: this is NOT yet a qualified opportunity. Sending a proposal now would be premature — it would land with the Director and likely die at the VP's desk. My next move is to ask the Director directly: "Before I put together pricing, who else inside your organization weighs in on something at this scope, and what does your typical approval process look like?" That question gets me Economic Buyer and Decision Process in one move.
"""

# Q4 (value messaging) — one strong answer per vertical so the PASS cohort
# does not read as copy-paste. None greets the SDR's own name (the example is
# addressed to a hypothetical prospect, not the candidate).
EXAM_PASS_VALUE_FINTECH = """### Q4 — Salesforce value messaging

For a VP of Sales at a mid-market fintech, I lead with their outcome, not features.

"The fintech revenue leaders I work with are usually under pressure to grow pipeline without loosening underwriting or risk controls. The teams that moved the needle used Sales Cloud's revenue intelligence to flag stalled deals two to three weeks earlier — one recovered about $3M in pipeline that quarter with the same headcount, and risk never had to slow them down. If that tension between growth and control sounds familiar, I'd want 30 minutes to see whether the same lever applies to your team."

I quantify ($3M, 2-3 weeks), tie the investment to a business outcome, and respect the risk constraint a fintech buyer cares about. I do not list features.
"""

EXAM_PASS_VALUE_FINTECH_BANKING = """### Q4 — Salesforce value messaging

For a VP of Sales at an EMEA banking or capital-markets firm, I anchor on a number their CFO already watches.

"Two capital-markets teams I worked with this year were leaking forecast accuracy because deal data lived in three systems. Once Sales Cloud became the single forecast everyone trusted, their commit-to-close slippage dropped from roughly 30% to under 15% in two quarters — same team, far fewer surprises in the board pack. If forecast trust is a live issue for you, that's the conversation I'd want to have."

I lead with a metric leadership tracks (forecast accuracy), quantify the change, and avoid a feature list.
"""

EXAM_PASS_VALUE_HEALTHCARE = """### Q4 — Salesforce value messaging

For a VP of Provider Operations in healthcare, I frame value in their language — staff and patient impact, not software.

"The provider-operations leaders I work with are usually trying to free clinical and admin staff from duplicate data entry. One regional system unified referrals and outreach on Sales Cloud and Data Cloud and cut manual reconciliation by about 11 hours a week per coordinator — time that went back to patient-facing work, with HIPAA controls intact. If that reclaimed-capacity story is relevant, I'd love 30 minutes."

I quantify (11 hours/week), tie it to a healthcare outcome, and name the HIPAA constraint a clinical buyer expects.
"""

EXAM_PASS_VALUE_MANUFACTURING = """### Q4 — Salesforce value messaging

For a CFO at a manufacturer, I lead with margin and data, not CRM features.

"The manufacturing CFOs I talk to are usually fighting customer data scattered across plant-level ERPs and a separate CRM. One built a single customer view on Data Cloud with Sales Cloud on top and shortened quote turnaround from days to hours, which protected roughly $5M in at-risk renewals last year. If fragmented customer data is costing you deals, that's the lever I'd want to explore."

I quantify ($5M, days to hours), tie it to a CFO's P&L concern, and ground it in their real systems problem.
"""

EXAM_PASS_DISCOVERY = """### Q5 — Discovery and questioning

Five open-ended discovery questions for a cold call with a Director of Operations at a regional healthcare provider:

1. "What's the operational metric your CEO is asking you to move this year, and how far are you from the number?"
2. "When you look across your ops team's day, where do you see the most time spent on work that doesn't create patient or business value?"
3. "Who else on your leadership team is feeling the same friction, and how would they describe it differently than you?"
4. "If you had to point to the single bottleneck that, if removed, would move the needle most on what you just described, what would it be?"
5. "What have you tried before that didn't stick, and what made it fall apart?"

Each opens the prospect rather than closing them. Each surfaces either pain (Q1, Q2), MEDDIC inputs (Q3 → Economic Buyer, Q5 → Decision Process), or context (Q4 → priority). None are yes/no.
"""

EXAM_BORDERLINE_DEFENSIVE = """### Q1 — Product knowledge accuracy

The Salesforce clouds are Sales Cloud, Service Cloud, Marketing Cloud, and Agentforce. Sales Cloud is for sales, Service Cloud is for service, Marketing Cloud is for marketing. Agentforce is the AI part.

### Q2 — Objection handling

When a prospect raises a price objection I would explain why Salesforce is worth the investment and try to overcome the objection by pointing out the ROI. I would emphasize the value.

### Q3 — MEDDIC application

The Director of Operations is the champion. Pain is implied. We should send the proposal and see if they sign.

### Q4 — Salesforce value messaging

Sales Cloud is a powerful platform with great features, AI capabilities, automation, and analytics. Companies see big productivity gains. The VP of Sales would benefit from increased rep productivity.

### Q5 — Discovery and questioning

I would ask: "Do you have a CRM?" "Are you happy with your current CRM?" "Would you like to learn more about Salesforce?" "Do you have budget for a new CRM?" "When are you looking to make a decision?"
"""

EXAM_FAIL_WRONG_PRODUCT = """### Q1 — Product knowledge accuracy

Sales Cloud is Salesforce's main product — it does everything: pipeline, customer service, marketing, you name it. Service Cloud is basically a newer name for Sales Cloud with some support features. Marketing Cloud is the newest Salesforce product, launched last year. Data Cloud is a database product. Agentforce is the AI feature.

### Q2 — Objection handling

If a prospect raises a price objection I would offer a 10% discount to get the deal closed faster. If they push back I'd offer 20%. The goal is to close the deal.

### Q3 — MEDDIC application

The Director is interested and engaged. They asked for a proposal. That means it's qualified. I would send the proposal immediately because asking too many questions slows the deal down. The Director can handle internal approvals on their side.

### Q4 — Salesforce value messaging

Sales Cloud has amazing features — AI-powered everything, automated workflows, mobile apps, and integration with thousands of other tools. The VP would love it because it's the best CRM on the market and used by Fortune 500 companies.

### Q5 — Discovery and questioning

"Are you looking for a new CRM?" "What's wrong with your current CRM?" "How big is your sales team?" "What's your budget?" "When can you decide?"
"""

EXAM_BORDERLINE_MEDDIC_PARTIAL = """### Q1 — Product knowledge accuracy

The core clouds and their business outcomes:
- **Sales Cloud** — pipeline and opportunity management; outcome is predictable revenue.
- **Service Cloud** — case management for post-sale support; outcome is lower cost per case.
- **Marketing Cloud** — multi-channel marketing automation; outcome is qualified pipeline from marketing.
- **Data Cloud** — unifies customer data across systems; outcome is one trusted customer view.
- **Agentforce** — AI layer running on top of the others; outcome is time saved on routine work.

### Q2 — Objection handling

On a price objection I would acknowledge the concern, then ask what's driving it — is it the absolute number, the timing, or a comparison against another vendor? Once I understand the real driver, I would reframe to the business outcome the prospect already mentioned in discovery. I would not lead with a discount on the first call.

### Q3 — MEDDIC application

Captured: Champion (the Director), partial pain.
Missing: Metrics (no quantified outcome stated), Economic Buyer (Director is not the EB at this spend level), Decision Process (no timeline or approval map), Decision Criteria (no documented requirements).

It's not qualified yet. I should ask the Director directly who else inside their organization weighs in on a purchase at this scope, and ask them to walk me through their typical approval process. That gets me EB and Decision Process at once.

(I note the question asks me to apply MEDDIC; I haven't yet quantified the metrics piece — I would push the Director to put a number on the pain in our next call.)

### Q4 — Salesforce value messaging

For a VP of Sales at a SaaS company, I would lead with pipeline pressure: "Three SaaS VPs of Sales I worked with this quarter were trying to grow pipeline 20% without adding headcount. The unlock was Sales Cloud's revenue intelligence layer flagging stalled deals earlier. One team recovered around $4M in pipeline with the same team size." I quantify and tie the investment to an outcome the VP already cares about.

### Q5 — Discovery and questioning

1. "What's the operational metric your CEO is asking you to move this year?"
2. "Where does your team spend time today that doesn't create real value?"
3. "Who else on your leadership team feels the same friction?"
4. "What's the single bottleneck that, if removed, would move the needle most?"
5. "What have you tried before that didn't stick — and why?"
"""

# Coaching note templates --------------------------------------------------

COACHING_NOTE_SOFT = """# Coaching note — call 1

**Score:** {score}/10
**Date:** {date}

What worked: opening was clear, set context about why the call. Good attempt at framing.

What to improve: discovery felt rushed; the SDR asked one question and then moved into pitch mode. The objection handling reverted to defending the product instead of using the Discover step. Next call, work on staying in question-mode for at least 3 turns after the prospect raises an objection.
"""

COACHING_NOTE_STRONG = """# Coaching note — call 1

**Score:** {score}/10
**Date:** {date}

What worked: discovery was excellent — five qualifying questions before any pitch language. Objection handling textbook: acknowledged, asked the real-concern question, reframed to value. Confirmed next step with a specific calendar time.

What to improve: small thing — the MEDDIC angle was implicit but never explicit. Next call, name the framework when scoping who else is in the decision (helps both you and the prospect).
"""

COACHING_NOTE_STRONG_HEALTHCARE = """# Coaching note — call 1

**Score:** {score}/10
**Date:** {date}

What worked: led with the provider's operational pressure before any product mention; four discovery questions surfaced the staffing pain in the buyer's own words. Handled the "we tried something like this" objection by acknowledging it and asking what specifically fell apart — a clean Discover step.

What to improve: strong call overall — tighten the close. You confirmed interest but left the next step soft ("I'll follow up"). Next time, lock a specific calendar slot before you hang up.
"""

COACHING_NOTE_STRONG_MANUFACTURING = """# Coaching note — call 1

**Score:** {score}/10
**Date:** {date}

What worked: opened on a concrete manufacturing pain (customer data split across plant ERPs) and earned the meeting by being specific. Good multi-threading instinct — asked who else touches the quoting process. Quantified the impact instead of pitching features.

What to improve: the MEDDIC scoping stayed implicit. Next call, explicitly map the Economic Buyer — a CFO-level spend needs the budget owner named, not assumed.
"""

# ---------------------------------------------------------------------------
# SDR cohort config
# ---------------------------------------------------------------------------

COHORT = [
    {
        "sdr_id": "SDR-001",
        "name": "Priya Sharma",
        "territory": "EMEA Healthcare",
        "experience_level": "entry",
        "vertical": "healthcare",
        "verdict": "BORDERLINE",
        "transcripts": [
            {"call": 1, "date": "2026-03-15", "template": TRANSCRIPT_BORDERLINE_DEFENSIVE,
             "scores": {"opening": 6, "discovery": 4, "objection_handling": 4, "close": 6}},
            {"call": 2, "date": "2026-04-12", "template": TRANSCRIPT_BORDERLINE_DEFENSIVE,
             "scores": {"opening": 7, "discovery": 5, "objection_handling": 5, "close": 7}},
        ],
        "exam_template": EXAM_BORDERLINE_DEFENSIVE,
        "exam_date": "2026-04-20",
        "coaching_note": {"call": 1, "score": 5.5, "date": "2026-03-18", "template": COACHING_NOTE_SOFT},
        "tutor_activity": {
            "top_topics": ["objection handling", "pricing", "discovery questions"],
            "flagged_gaps": ["acknowledge-discover-deliver pattern", "open-ended question structure"],
        },
        "prospect_name": "Director of Ops at Meridian Health",
        "gap_analysis": {
            "scores": [7, 5, 5, 6, 6],
            "overall": "BORDERLINE",
            "rationale": "Priya shows competent product knowledge and a workable value framing but reverts to defending product features when objections surface, and her discovery questioning leans closed and superficial. The 5s on objection handling and MEDDIC keep her in BORDERLINE — trainer should weigh trajectory across her two simulation calls (improving) against the gaps on the exam.",
            "evidence": {
                "product_knowledge_accuracy": ("Sales Cloud is for sales, Service Cloud is for service, Marketing Cloud is for marketing.",
                                              "Identifies the clouds correctly but with no business-outcome framing.",
                                              "Product names without the 'so what' — outcome language missing.",
                                              "Pair her with the value-messaging practice module."),
                "objection_handling": ("I would explain why Salesforce is worth the investment and try to overcome the objection by pointing out the ROI.",
                                       "Skips the Defuse and Discover steps and goes straight to Deliver — defensive rather than curious.",
                                       "No acknowledgement, no clarifying question; argues instead of asks.",
                                       "Objection roleplay focused on the Discover step — three sessions minimum."),
                "meddic_application": ("The Director of Operations is the champion. Pain is implied. We should send the proposal and see if they sign.",
                                       "Conflates a friendly contact with a qualified opportunity and skips Economic Buyer, Metrics, and Decision Process entirely.",
                                       "Treats champion presence as sufficient signal — this is exactly the pattern that produces unqualified AE handoffs.",
                                       "MEDDIC qualification drills, with specific focus on the Economic-Buyer-vs-Champion distinction."),
                "salesforce_value_messaging": ("Sales Cloud is a powerful platform with great features, AI capabilities, automation, and analytics.",
                                               "Leads with features rather than the VP's business outcome; no quantification.",
                                               "Feature dumping; nothing tied back to the prospect's stated priorities.",
                                               "Value messaging practice tied to specific personas."),
                "discovery_and_questioning": ("Do you have a CRM? Are you happy with your current CRM? Would you like to learn more about Salesforce?",
                                              "All closed yes/no questions and all about Salesforce rather than the prospect.",
                                              "Discovery is a checklist of qualifying questions about Salesforce, not the prospect's world.",
                                              "Discovery question bank practice; active-listening drills."),
            },
            "confidence": 0.78,
        },
    },
    {
        "sdr_id": "SDR-002",
        "name": "Marcus Chen",
        "territory": "AMER FinTech",
        "experience_level": "mid",
        "vertical": "fintech",
        "verdict": "PASS",
        "transcripts": [
            {"call": 1, "date": "2026-03-18", "template": TRANSCRIPT_PASS_STRONG,
             "scores": {"opening": 8, "discovery": 9, "objection_handling": 8, "close": 8}},
        ],
        "exam_template": EXAM_PASS_PRODUCT + "\n" + EXAM_PASS_OBJECTION + "\n" + EXAM_PASS_MEDDIC + "\n" + EXAM_PASS_VALUE_FINTECH + "\n" + EXAM_PASS_DISCOVERY,
        "exam_date": "2026-04-22",
        "coaching_note": {"call": 1, "score": 8.5, "date": "2026-03-20", "template": COACHING_NOTE_STRONG},
        "tutor_activity": {
            "top_topics": ["MEDDIC", "multi-threading", "value messaging"],
            "flagged_gaps": [],
        },
        "prospect_name": "Director of Ops at NorthStar Capital",
        "gap_analysis": {
            "scores": [9, 8, 9, 9, 9],
            "overall": "PASS",
            "rationale": "Marcus consistently scores at or above the passing bar across all five dimensions. Objection handling shows clear use of the Defuse-Discover-Deliver pattern, MEDDIC application is rigorous (correctly identifies the EB gap in the qualification scenario), and discovery is genuinely open-ended. Ready for live calls with real prospects.",
            "evidence": {
                "product_knowledge_accuracy": ("Sales Cloud is built around the Opportunity object, Service Cloud around the Case object. I would not blur them.",
                                              "Distinguishes the clouds at the schema level and ties each to a business outcome rather than features.",
                                              "Minor — could add nuance on Data Cloud's role in the unified customer profile but not a real gap.",
                                              "Promote into a peer-coaching role for incoming hires on product fluency."),
                "objection_handling": ("Defuse — Acknowledge the concern and the emotion. Thank you for raising it directly. Discover — Ask an open-ended question to surface what's actually behind the objection.",
                                       "Names all three steps, includes a specific Discover question, and frames Deliver as reframing not arguing.",
                                       "Minor — example was generic; a vertical-specific example would be even sharper.",
                                       "Roleplay with FinTech-specific objections (regulatory, security review timing) for additional fluency."),
                "meddic_application": ("Verdict: this is NOT yet a qualified opportunity. Sending a proposal now would be premature — it would land with the Director and likely die at the VP's desk.",
                                       "Correctly identifies the EB gap, names Metrics and Decision Process as the other missing pieces, and proposes a single question that unlocks two of them at once.",
                                       "No real gap — this is a textbook qualification call.",
                                       "Continue current trajectory."),
                "salesforce_value_messaging": ("One team recovered roughly $4M in pipeline they would have otherwise lost to neglect, with the same team size.",
                                               "Quantifies, ties to outcome (pipeline recovery with same headcount), avoids feature language.",
                                               "Minor — could add a falsifiable citation source for the $4M number.",
                                               "Continue current trajectory; consider mentoring others on value framing."),
                "discovery_and_questioning": ("What's the operational metric your CEO is asking you to move this year, and how far are you from the number?",
                                              "Five truly open-ended questions, each surfacing either pain, MEDDIC inputs, or priority. No yes/no.",
                                              "No real gap.",
                                              "Continue current trajectory."),
            },
            "confidence": 0.92,
        },
    },
    {
        "sdr_id": "SDR-003",
        "name": "Aisha Patel",
        "territory": "AMER SaaS",
        "experience_level": "entry",
        "vertical": "saas",
        "verdict": "FAIL",
        "transcripts": [
            {"call": 1, "date": "2026-03-16", "template": TRANSCRIPT_FAIL_FEATURE_DUMP,
             "scores": {"opening": 4, "discovery": 3, "objection_handling": 2, "close": 3}},
        ],
        "exam_template": EXAM_FAIL_WRONG_PRODUCT,
        "exam_date": "2026-04-21",
        "coaching_note": {"call": 1, "score": 3.5, "date": "2026-03-19", "template": COACHING_NOTE_SOFT},
        "tutor_activity": {
            "top_topics": ["closing techniques", "discount authority"],
            "flagged_gaps": ["product fundamentals", "qualification framework", "MEDDIC"],
        },
        "prospect_name": "VP of Sales at BrightPath SaaS",
        "gap_analysis": {
            "scores": [2, 3, 2, 3, 3],
            "overall": "FAIL",
            "rationale": "Aisha confuses Service Cloud with Sales Cloud, claims Marketing Cloud launched 'last year' (it's been around over a decade), and treats champion presence as sufficient to send a proposal. Objection handling is to discount; discovery is closed and pitch-driven. This is a fail on every dimension and should not advance to live calls without significant remediation.",
            "evidence": {
                "product_knowledge_accuracy": ("Sales Cloud is Salesforce's main product — it does everything: pipeline, customer service, marketing. Service Cloud is basically a newer name for Sales Cloud.",
                                              "Conflates Sales Cloud and Service Cloud, claims Marketing Cloud is brand new, and treats every cloud as interchangeable.",
                                              "Cannot distinguish core products at the schema or business-outcome level — fundamental gap.",
                                              "Targeted product modules for every cloud; do not advance until product fundamentals are solid."),
                "objection_handling": ("If a prospect raises a price objection I would offer a 10% discount to get the deal closed faster.",
                                       "Skips Defuse and Discover entirely; goes straight to discount as the lever, which trains the prospect to wait for the next discount.",
                                       "Inverts the rubric — discount is the wrong tool and undermines value-based positioning.",
                                       "Re-do the objection roleplay program from the start; supervised practice with the SDR manager."),
                "meddic_application": ("The Director is interested and engaged. They asked for a proposal. That means it's qualified.",
                                       "Sends proposals to deals with no EB, no quantified pain, no decision process — exactly the pattern that produces failed AE handoffs.",
                                       "Champion-equals-qualified is the most common new-SDR mistake and is fully present here.",
                                       "Mandatory MEDDIC qualification drills with weekly check-ins until consistent."),
                "salesforce_value_messaging": ("Sales Cloud has amazing features — AI-powered everything, automated workflows, mobile apps, and integration with thousands of other tools.",
                                               "Pure feature dump with no quantified outcome and no tie to the prospect's stated priorities.",
                                               "Cannot articulate value beyond 'best CRM, Fortune 500 uses it.'",
                                               "Value messaging practice from the ground up; would benefit from shadowing a senior SDR on three live calls before next certification attempt."),
                "discovery_and_questioning": ("Are you looking for a new CRM? What's wrong with your current CRM? How big is your sales team? What's your budget?",
                                              "Four of five questions are closed yes/no or about Salesforce rather than the prospect's situation.",
                                              "Discovery is product-centric not prospect-centric.",
                                              "Discovery question bank practice with daily roleplays for two weeks."),
            },
            "confidence": 0.94,
        },
    },
    {
        "sdr_id": "SDR-004",
        "name": "Diego Rodriguez",
        "territory": "EMEA Retail",
        "experience_level": "entry",
        "vertical": "retail",
        "verdict": "BORDERLINE",
        "transcripts": [
            {"call": 1, "date": "2026-03-17", "template": TRANSCRIPT_BORDERLINE_MEDDIC_PARTIAL,
             "scores": {"opening": 8, "discovery": 7, "objection_handling": 6, "close": 7}},
        ],
        "exam_template": EXAM_BORDERLINE_MEDDIC_PARTIAL,
        "exam_date": "2026-04-23",
        "coaching_note": None,
        "tutor_activity": {
            "top_topics": ["MEDDIC qualification", "economic buyer", "decision process"],
            "flagged_gaps": ["Metrics quantification"],
        },
        "prospect_name": "Director of Ops at StonePath Retail",
        "gap_analysis": {
            "scores": [8, 7, 6, 8, 7],
            "overall": "BORDERLINE",
            "rationale": "Diego's pitch is solid and his discovery is genuinely open-ended. The one gap is on MEDDIC — he correctly identifies Economic Buyer and Decision Process gaps, but skips Metrics quantification, which the rubric flags as the single most common cause of failed AE handoffs. With one targeted coaching session he is at a PASS bar; recommend trainer review with a plan rather than a no-go.",
            "evidence": {
                "product_knowledge_accuracy": ("Sales Cloud — pipeline and opportunity management; outcome is predictable revenue. Service Cloud — case management for post-sale support; outcome is lower cost per case.",
                                              "Pairs each cloud with a business outcome and distinguishes them correctly.",
                                              "Minor — could go deeper on Data Cloud's role in unified customer view.",
                                              "Optional: short reading on Data Cloud architecture patterns."),
                "objection_handling": ("On a price objection I would acknowledge the concern, then ask what's driving it — is it the absolute number, the timing, or a comparison against another vendor?",
                                       "Names Defuse and Discover and routes through them in order; explicitly avoids leading with a discount.",
                                       "Slightly mechanical — could feel more conversational; missed an opportunity to reframe in his transcript when the prospect mentioned 'paperwork.'",
                                       "Three sessions of conversational objection roleplay focused on Deliver-step fluency."),
                "meddic_application": ("(I note the question asks me to apply MEDDIC; I haven't yet quantified the metrics piece — I would push the Director to put a number on the pain in our next call.)",
                                       "Correctly identifies EB and Decision Process gaps but openly admits he skipped Metrics quantification — the rubric explicitly weights this dimension heavily because poor qualification is the most common cause of failed handoffs.",
                                       "Missing Metrics quantification is the borderline-not-fail line; he sees the gap but didn't close it.",
                                       "One targeted coaching session on quantifying pain ('what does this cost you in real dollars or hours'); roleplay with three retail-specific examples."),
                "salesforce_value_messaging": ("Three SaaS VPs of Sales I worked with this quarter were trying to grow pipeline 20% without adding headcount. The unlock was Sales Cloud's revenue intelligence layer flagging stalled deals earlier.",
                                               "Quantifies, ties to outcome the VP cares about, avoids feature language. Strong dimension.",
                                               "Minor — example was SaaS, not Retail (his territory). Worth tailoring.",
                                               "Continue current trajectory; build a Retail-specific value-messaging pattern."),
                "discovery_and_questioning": ("What's the operational metric your CEO is asking you to move this year? Where does your team spend time today that doesn't create real value?",
                                              "Five open-ended questions covering pain, MEDDIC inputs, and context.",
                                              "Minor — could be more retail-specific to land harder with his territory.",
                                              "Optional: build a vertical-specific discovery question bank."),
            },
            "confidence": 0.82,
        },
    },
    {
        "sdr_id": "SDR-005",
        "name": "Sarah Kim",
        "territory": "AMER Healthcare",
        "experience_level": "mid",
        "vertical": "healthcare",
        "verdict": "PASS",
        "transcripts": [
            {"call": 1, "date": "2026-03-19", "template": TRANSCRIPT_PASS_DISCOVERY,
             "scores": {"opening": 8, "discovery": 9, "objection_handling": 8, "close": 9}},
        ],
        "exam_template": EXAM_PASS_PRODUCT + "\n" + EXAM_PASS_OBJECTION + "\n" + EXAM_PASS_MEDDIC + "\n" + EXAM_PASS_VALUE_HEALTHCARE + "\n" + EXAM_PASS_DISCOVERY,
        "exam_date": "2026-04-24",
        "coaching_note": {"call": 1, "score": 8.5, "date": "2026-03-21", "template": COACHING_NOTE_STRONG_HEALTHCARE},
        "tutor_activity": {
            "top_topics": ["discovery", "MEDDIC", "healthcare compliance"],
            "flagged_gaps": [],
        },
        "prospect_name": "VP of Provider Operations at Tula Health",
        "gap_analysis": {
            "scores": [8, 8, 9, 8, 9],
            "overall": "PASS",
            "rationale": "Sarah's discovery is the strongest in the cohort — she names MEDDIC explicitly and uses it as a structuring lens during the conversation, not as a checklist afterward. Objection handling and value messaging are at the passing bar. Ready for live calls; would be a strong peer-coach.",
            "evidence": {
                "product_knowledge_accuracy": ("Sales Cloud — pipeline and opportunity management. Service Cloud — case management and customer service.",
                                              "Clean, outcome-framed descriptions of each cloud.",
                                              "Minor — could mention healthcare-specific compliance overlays.",
                                              "Optional: HIPAA-aware selling deep-dive."),
                "objection_handling": ("Defuse — Acknowledge the concern and the emotion. Discover — Ask an open-ended question to surface what's actually behind the objection.",
                                       "Named pattern with a specific clarifying question.",
                                       "Minor — example was generic; vertical-specific examples would be sharper.",
                                       "Continue trajectory; mentor others on the Deliver step."),
                "meddic_application": ("That's MEDDIC, basically — economic buyer and champion missing. Are you using a structured framework today?",
                                       "Names MEDDIC explicitly in the conversation and uses it as a tool, not a label.",
                                       "No gap.",
                                       "Continue trajectory."),
                "salesforce_value_messaging": ("Three SaaS VPs of Sales I worked with this quarter were trying to grow pipeline 20% without adding headcount.",
                                               "Quantifies, ties to outcome.",
                                               "Minor — could be more Healthcare-specific.",
                                               "Build a Healthcare-specific value-messaging pattern."),
                "discovery_and_questioning": ("What's the operational metric your CEO is asking you to move this year, and how far are you from the number?",
                                              "Five genuinely open-ended questions, surfacing pain, priority, and MEDDIC inputs.",
                                              "No real gap.",
                                              "Continue trajectory; consider co-leading a discovery workshop."),
            },
            "confidence": 0.90,
        },
    },
    {
        "sdr_id": "SDR-006",
        "name": "Liam O'Brien",
        "territory": "EMEA FinTech",
        "experience_level": "senior",
        "vertical": "fintech",
        "verdict": "PASS",
        "transcripts": [
            {"call": 1, "date": "2026-03-20", "template": TRANSCRIPT_PASS_VALUE_MESSAGING,
             "scores": {"opening": 8, "discovery": 8, "objection_handling": 8, "close": 9}},
        ],
        "exam_template": EXAM_PASS_PRODUCT + "\n" + EXAM_PASS_OBJECTION + "\n" + EXAM_PASS_MEDDIC + "\n" + EXAM_PASS_VALUE_FINTECH_BANKING + "\n" + EXAM_PASS_DISCOVERY,
        "exam_date": "2026-04-25",
        "coaching_note": None,
        "tutor_activity": {
            "top_topics": ["value framing", "Data Cloud", "executive pitching"],
            "flagged_gaps": [],
        },
        "prospect_name": "VP of Sales at Aldgate FinTech",
        "gap_analysis": {
            "scores": [9, 8, 8, 9, 8],
            "overall": "PASS",
            "rationale": "Liam's value messaging is the strongest in the cohort — quantifies cleanly, names specific peer outcomes, and frames the investment as a return rather than a cost. Senior-level fluency across all five dimensions. Ready for live calls.",
            "evidence": {
                "product_knowledge_accuracy": ("Sales Cloud is built around the Opportunity object, Service Cloud around the Case object.",
                                              "Schema-level distinction; outcome framing per cloud.",
                                              "No real gap.",
                                              "Continue trajectory."),
                "objection_handling": ("Defuse — Acknowledge the concern. Discover — Ask an open-ended question. Deliver — reframe to value.",
                                       "Names and uses the pattern; explicit avoidance of discounting first.",
                                       "Minor — could go deeper on regulatory objection variants for FinTech.",
                                       "FinTech-specific objection library practice."),
                "meddic_application": ("Verdict: this is NOT yet a qualified opportunity. Sending a proposal now would be premature.",
                                       "Correctly identifies EB gap and proposes a question that unlocks two missing dimensions at once.",
                                       "No real gap.",
                                       "Continue trajectory."),
                "salesforce_value_messaging": ("Two of your FinTech peers I worked with last quarter were stuck on the same math. Both used Sales Cloud + Data Cloud to enrich existing accounts. One added $8M in pipeline in two quarters with the same headcount.",
                                               "Quantifies (4x time, $8M, 8 weeks), names peer examples, frames as investment with return.",
                                               "No real gap.",
                                               "Continue trajectory; lead value-messaging clinics for newer SDRs."),
                "discovery_and_questioning": ("How are you thinking about getting there? Is that work your team has the capacity for, or is that a blocker?",
                                              "Open-ended, surfaces both pain and feasibility.",
                                              "Minor — could ask one more question about Decision Process explicitly.",
                                              "Continue trajectory."),
            },
            "confidence": 0.89,
        },
    },
    {
        "sdr_id": "SDR-007",
        "name": "Yuki Tanaka",
        "territory": "AMER Manufacturing",
        "experience_level": "mid",
        "vertical": "manufacturing",
        "verdict": "PASS",
        "transcripts": [
            {"call": 1, "date": "2026-03-21", "template": TRANSCRIPT_PASS_PRODUCT_FLUENCY,
             "scores": {"opening": 8, "discovery": 8, "objection_handling": 7, "close": 8}},
        ],
        "exam_template": EXAM_PASS_PRODUCT + "\n" + EXAM_PASS_OBJECTION + "\n" + EXAM_PASS_MEDDIC + "\n" + EXAM_PASS_VALUE_MANUFACTURING + "\n" + EXAM_PASS_DISCOVERY,
        "exam_date": "2026-04-26",
        "coaching_note": {"call": 1, "score": 7.8, "date": "2026-03-23", "template": COACHING_NOTE_STRONG_MANUFACTURING},
        "tutor_activity": {
            "top_topics": ["Data Cloud", "manufacturing ERP integration", "multi-stakeholder selling"],
            "flagged_gaps": [],
        },
        "prospect_name": "CFO at HighRidge Manufacturing",
        "gap_analysis": {
            "scores": [9, 7, 8, 8, 8],
            "overall": "PASS",
            "rationale": "Yuki's product fluency is exceptional — explicitly distinguishes when Data Cloud is the right entry point vs Sales Cloud and resists the temptation to pitch Service Cloud when it's not relevant. Solid across the other dimensions. Ready for live calls.",
            "evidence": {
                "product_knowledge_accuracy": ("That's a Data Cloud problem more than a Sales Cloud problem — you'd want a single source of truth that pulls plant-level inventory into the rep's quote workflow. Service Cloud isn't relevant here unless you've got a post-sale case-routing problem too.",
                                              "Knows when each cloud is the right tool and when it isn't; resists feature-stacking.",
                                              "No real gap.",
                                              "Continue trajectory; consider mentoring on product positioning."),
                "objection_handling": ("Acknowledged the concern and asked the real-concern question.",
                                       "Pattern applied cleanly; could stretch on more advanced objection variants.",
                                       "Minor — was a smooth conversation without major objection pressure.",
                                       "Roleplay against advanced objections (CFO-level scrutiny, multi-vendor comparison)."),
                "meddic_application": ("What does the decision process look like for something at this scope — IT, procurement, line of business?",
                                       "Maps Decision Process explicitly and brings the right roles into the next conversation.",
                                       "Minor — could quantify Metrics more aggressively.",
                                       "One coaching session on pain quantification."),
                "salesforce_value_messaging": ("Sold the outcome (consolidated quote accuracy) rather than features.",
                                               "Outcome-led; names the architecture as a path to the outcome, not as the value itself.",
                                               "Minor — could quantify time saved more precisely.",
                                               "Build a Manufacturing-specific value pattern with hours-saved numbers."),
                "discovery_and_questioning": ("What hurts most — quote accuracy across plants, or service handoffs when an order arrives?",
                                              "Forced-choice question that surfaces the real pain quickly without being yes/no.",
                                              "Minor — five questions would have been even stronger.",
                                              "Continue trajectory."),
            },
            "confidence": 0.87,
        },
    },
]


# ---------------------------------------------------------------------------
# Writing helpers
# ---------------------------------------------------------------------------

def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _build_record(sdr: dict, transcript_files: list[str]) -> dict:
    events = []
    for i, t in enumerate(sdr["transcripts"]):
        events.append({
            "phase": "simulation",
            "call": t["call"],
            "date": t["date"],
            "scores": t["scores"],
            "transcript_file": transcript_files[i],
        })
    events.append({
        "phase": "exam",
        "date": sdr["exam_date"],
        "qa_file": f"{sdr['sdr_id']}/certification-exam.md",
    })
    if sdr["coaching_note"]:
        cn = sdr["coaching_note"]
        events.append({
            "phase": "coaching_note",
            "call": cn["call"],
            "date": cn["date"],
            "score": cn["score"],
            "note_file": f"{sdr['sdr_id']}/coaching-note-1.md",
        })
    if sdr["tutor_activity"]:
        events.append({
            "phase": "tutor_activity",
            "top_topics": sdr["tutor_activity"]["top_topics"],
            "flagged_gaps": sdr["tutor_activity"]["flagged_gaps"],
        })
    return {
        "sdr_id": sdr["sdr_id"],
        "name": sdr["name"],
        "cohort": COHORT_LABEL,
        "territory": sdr["territory"],
        "experience_level": sdr["experience_level"],
        "events": events,
    }


def _verdict_for(score: int) -> str:
    if score <= 4:
        return "fail"
    if score <= 6:
        return "borderline"
    return "pass"


DIMENSIONS = (
    "product_knowledge_accuracy",
    "objection_handling",
    "meddic_application",
    "salesforce_value_messaging",
    "discovery_and_questioning",
)

DIMENSION_LABELS = {
    "product_knowledge_accuracy": "Product knowledge accuracy",
    "objection_handling": "Objection handling (Defuse, Discover, Deliver)",
    "meddic_application": "MEDDIC framework application",
    "salesforce_value_messaging": "Salesforce value messaging",
    "discovery_and_questioning": "Discovery and questioning",
}


def _build_gap_analysis_envelope(sdr: dict, record: dict) -> dict:
    ga = sdr["gap_analysis"]
    findings = {}
    for dim_id, score in zip(DIMENSIONS, ga["scores"]):
        evidence_quote, rationale, gap, action = ga["evidence"][dim_id]
        findings[dim_id] = {
            "score": score,
            "verdict": _verdict_for(score),
            "evidence_quote": evidence_quote,
            "rationale": rationale,
            "gap_to_close": gap,
            "coaching_action": action,
            "label": DIMENSION_LABELS[dim_id],
        }
    weakest = min(findings.items(), key=lambda kv: kv[1]["score"])[0]
    review_reasons: list[str] = []
    if ga["overall"] != "PASS":
        review_reasons.append(
            f"server-computed overall recommendation is {ga['overall']} — trainer review required"
        )
    return {
        "status": "needs_review" if review_reasons else "ok",
        "next_action": "done",
        "confidence": ga["confidence"],
        "review_required": bool(review_reasons),
        "artifact_refs": ["01_certification_gap_analysis.md"],
        "outputs": {
            "sdr_id": sdr["sdr_id"],
            "sdr_name": sdr["name"],
            "cohort": COHORT_LABEL,
            "territory": sdr["territory"],
            "overall_recommendation": ga["overall"],
            "llm_overall_recommendation": ga["overall"],
            "overall_rationale": ga["rationale"],
            "weakest_dimension": weakest,
            "dimension_findings": findings,
            "review_reasons": review_reasons,
            "retrieved_docs": ["certification_rubric.md", "certification_questions.md"],
            "sources": [
                {
                    "doc_name": "certification_rubric.md",
                    "passage": "Passing bar: an SDR should score 7 or above on every dimension. A score of 5-6 on any one dimension is a borderline result and requires trainer review. A score of 4 or below on any dimension is a fail on that dimension regardless of the others.",
                    "score": 0.92,
                    "weak": False,
                },
                {
                    "doc_name": "certification_rubric.md",
                    "passage": "MEDDIC framework application — Common gap: SDRs conflate a helpful contact with the economic buyer, and book meetings that the AE later rejects. Coaching action: MEDDIC qualification drills.",
                    "score": 0.88,
                    "weak": False,
                },
                {
                    "doc_name": "certification_questions.md",
                    "passage": "Q3 — MEDDIC framework application. Identify which elements are captured and which are missing. Would you call this a qualified opportunity ready for an AE handoff, or not?",
                    "score": 0.81,
                    "weak": False,
                },
            ],
            "generated_at": _now_iso(),
        },
        "error": None,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def seed(force: bool = False) -> int:
    """Write all 7 SDRs. Returns count of new records actually written.

    Skips any sdr_id whose <sdr_id>.json already exists unless force=True.
    """
    SDR_RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    new_count = 0

    for sdr in COHORT:
        sdr_id = sdr["sdr_id"]
        json_path = SDR_RECORDS_DIR / f"{sdr_id}.json"
        if json_path.exists() and not force:
            print(f"  skip {sdr_id} — already exists", file=sys.stderr)
            continue

        sdr_dir = SDR_RECORDS_DIR / sdr_id
        sdr_dir.mkdir(parents=True, exist_ok=True)

        transcript_files: list[str] = []
        for t in sdr["transcripts"]:
            fname = f"call-{t['call']}-transcript.md"
            content = t["template"].format(
                prospect_name=sdr["prospect_name"],
                vertical=sdr["vertical"],
            )
            _write_text(sdr_dir / fname, content)
            transcript_files.append(f"{sdr_id}/{fname}")

        exam_content = sdr["exam_template"].format(
            first_name=sdr["name"].split()[0],
        )
        _write_text(sdr_dir / "certification-exam.md", exam_content)

        if sdr["coaching_note"]:
            cn = sdr["coaching_note"]
            cn_content = cn["template"].format(score=cn["score"], date=cn["date"])
            _write_text(sdr_dir / "coaching-note-1.md", cn_content)

        record = _build_record(sdr, transcript_files)
        _write_json(json_path, record)

        envelope = _build_gap_analysis_envelope(sdr, record)
        _write_json(sdr_dir / "gap_analysis.json", envelope)

        print(f"  wrote {sdr_id} ({sdr['name']}) — verdict {sdr['verdict']}", file=sys.stderr)
        new_count += 1

    return new_count


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Seed the demo SDR cohort under data/sdr_records/")
    parser.add_argument("--force", action="store_true", help="overwrite existing SDR records")
    args = parser.parse_args()
    n = seed(force=args.force)
    print(f"Done. {n} record(s) written. Cohort dir: {SDR_RECORDS_DIR}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
