"""
Hardcoded synthetic data for MOCK_MODE.

All content is fictional / instructional — no real Salesforce customer or
employee data. Calibrated against Bridge Group SDR benchmarks and TOPO research.

Structure mirrors the real API response shapes so flipping MOCK_MODE = False
in main.py requires zero frontend changes.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# AI TUTOR — 5 Q&A pairs  (Feature 1, Step 4)
# ─────────────────────────────────────────────────────────────────────────────

MOCK_QA_PAIRS: list[dict] = [
    {
        "keywords": [
            "meddic",
            "qualification",
            "qualify",
            "framework",
            "metrics",
            "economic buyer",
            "decision criteria",
        ],
        "question": "What is the MEDDIC qualification framework?",
        "answer": (
            "MEDDIC is Salesforce's primary deal-qualification framework for enterprise sales. [1]\n\n"
            '**M — Metrics:** Quantify the economic impact. Ask "What does this problem cost you annually?" '
            "Get a number. Without metrics you have a conversation, not a deal. [1]\n\n"
            "**E — Economic Buyer:** The person who controls budget and can sign the contract. "
            "Champion ≠ Economic Buyer — you need access to both. [2]\n\n"
            "**D — Decision Criteria:** How does the prospect evaluate vendors? Technical fit? Price? "
            "Implementation timeline? Know their scorecard before you present. [1]\n\n"
            "**D — Decision Process:** Who is involved, in what order, and what does approval look like? "
            "Map every step before your final proposal. [2]\n\n"
            "**I — Identify Pain:** The business pain that makes the deal urgent. "
            'Quantified pain creates urgency — "nice to have" never closes. [1]\n\n'
            "**C — Champion:** Your internal advocate who sells for you when you're not in the room. "
            "They must have influence and a personal win tied to your solution. [3]\n\n"
            "**Action:** On your next discovery call, explicitly ask about each MEDDIC component "
            "and log gaps in Salesforce immediately after."
        ),
        "sources": [
            {"source": "salesforce_playbook", "type": "product_doc", "score": 0.94},
            {
                "source": "trailhead_enterprise_sales",
                "type": "training_module",
                "score": 0.91,
            },
            {"source": "approved_qa", "type": "qa_pair", "score": 0.88},
        ],
        "confidence_score": 0.94,
        "token_count": 312,
    },
    {
        "keywords": [
            "send me an email",
            "email objection",
            "just email",
            "email me",
            "send info",
        ],
        "question": "How do I handle the 'send me an email' objection?",
        "answer": (
            '"Send me an email" almost always means "I\'m trying to get off this call." '
            "Your goal is to preserve the conversation, not comply immediately. [1]\n\n"
            '**Step 1 — Acknowledge:** "Absolutely, happy to send something over."\n\n'
            '**Step 2 — Qualify before you hang up:** "So I can make it worth your time — '
            'is [specific pain point you researched] something your team is actively working through?"\n\n'
            "**Step 3 — Branch on their answer:**\n"
            "- If they engage → book 15 minutes before ending the call\n"
            '- If they repeat "just email" → confirm address, send within 5 minutes, '
            "reference the call in the subject line [2]\n\n"
            "**What to send:** 3 bullets max. Lead with their industry pain, "
            "connect to one specific outcome Salesforce drove for a peer company, "
            "close with a calendar link. Never send a feature dump. [2]\n\n"
            '**Action:** Draft your standard "send me an email" follow-up template today '
            "and get it reviewed by your manager before your next call block."
        ),
        "sources": [
            {
                "source": "objection_handling_guide",
                "type": "coaching_note",
                "score": 0.92,
            },
            {"source": "approved_qa", "type": "qa_pair", "score": 0.89},
        ],
        "confidence_score": 0.92,
        "token_count": 278,
    },
    {
        "keywords": [
            "champion",
            "economic buyer",
            "difference",
            "sponsor",
            "stakeholder",
            "eb",
        ],
        "question": "What's the difference between a champion and an economic buyer?",
        "answer": (
            "These are two of the most important — and most confused — roles in enterprise deals. [1]\n\n"
            "**Champion:** An internal advocate inside the prospect account who personally benefits "
            "from your solution and will sell for you internally. They attend demos, prep the room, "
            "and fight for budget. Champions have influence but often lack signing authority. [1]\n\n"
            "**Economic Buyer (EB):** The person with unilateral budget authority who can say yes or no "
            "to the final contract. In mid-market Salesforce deals this is typically a VP of Sales, "
            "CRO, or CFO. The EB rarely engages early but is always the last signature. [2]\n\n"
            "**The critical insight:** A champion who cannot get you to the EB is a blocked deal. "
            "Your job is to use your champion to gain EB access before your competitor does. [1]\n\n"
            "**Red flag:** If you have never spoken to the EB after three or more months in a deal, "
            "it is likely stalled or at risk. [2]\n\n"
            "**Action:** Map your top 3 active opportunities right now. "
            "Do you know who the EB is? Have you spoken directly with them?"
        ),
        "sources": [
            {"source": "salesforce_playbook", "type": "product_doc", "score": 0.93},
            {
                "source": "trailhead_enterprise_sales",
                "type": "training_module",
                "score": 0.90,
            },
        ],
        "confidence_score": 0.93,
        "token_count": 256,
    },
    {
        "keywords": [
            "touches",
            "unresponsive",
            "inactive",
            "follow up",
            "cadence",
            "sequence",
            "attempts",
            "how many",
        ],
        "question": "How many touches before marking a prospect unresponsive?",
        "answer": (
            "The Bridge Group's 2023 SDR benchmarks set the standard: "
            "**8–12 touches across 2–3 weeks** before marking a prospect Inactive in Salesforce. [1]\n\n"
            "**Recommended 12-touch sequence:**\n"
            "- Days 1–3: Personalized email · VM + no-VM call · LinkedIn connect request\n"
            "- Days 4–7: Case study or insight email · Call · LinkedIn message\n"
            "- Days 8–12: Breakup-style email · Final call · Final LinkedIn note [1]\n\n"
            "**Channel mix matters:** SDRs using 3+ channels have 3× higher connect rates "
            "than email-only reps (TOPO, 2023). [2]\n\n"
            '**Breakup email is not optional:** Always send a final "closing your file" email. '
            "15–20% of responses come from breakup emails because they create urgency. [2]\n\n"
            "**After 12 touches with zero response:** Mark Inactive, set a 90-day Salesforce task "
            "to re-engage when a trigger event fires — funding round, leadership change, tech news. [1]\n\n"
            "**Action:** Confirm your Salesforce sequence is set to 12 touches. "
            "If not, ask your manager to update the cadence today."
        ),
        "sources": [
            {"source": "bridge_group_benchmarks", "type": "handoff_doc", "score": 0.91},
            {"source": "sdr_playbook_2024", "type": "product_doc", "score": 0.88},
        ],
        "confidence_score": 0.91,
        "token_count": 289,
    },
    {
        "keywords": [
            "cfo",
            "cold call",
            "open",
            "c-suite",
            "c-level",
            "executive",
            "finance",
            "chief financial",
        ],
        "question": "How to open a cold call with a CFO?",
        "answer": (
            "CFOs receive 50+ cold calls per week. You have 7 seconds before they hang up. "
            "Standard openers don't work at this level. [1]\n\n"
            "**What works:**\n"
            '1. State your name and company immediately — no warm-up, no "How are you?"\n'
            "2. Lead with a financial outcome, never a feature: "
            '"We helped [similar company] cut their revenue close cycle from 5 days to same-day."\n'
            '3. Ask one sharp question: "Is that a priority for your finance org this quarter?"\n'
            "4. If yes: offer two specific time slots — "
            '"I have 15 minutes Tuesday at 2pm or Thursday at 10am. Which works?" [2]\n\n'
            "**What not to do:**\n"
            '- Never open with "How are you?" — it signals you\'re stalling\n'
            '- Never say "I know you\'re busy" — it gives them permission to exit\n'
            "- Never lead with Salesforce features — CFOs buy outcomes, not tools [1]\n\n"
            '**Proven script:** "Hi [Name], this is [You] from Salesforce. '
            "We just wrapped a project helping [Peer Company] close their revenue reporting gap — "
            'took them from 5-day cycles to same-day. Worth 15 minutes next week?" [2]\n\n'
            "**Action:** Write and rehearse 3 CFO-specific openers for your territory's "
            "top vertical before your next executive outreach block."
        ),
        "sources": [
            {
                "source": "executive_selling_guide",
                "type": "coaching_note",
                "score": 0.90,
            },
            {"source": "approved_qa", "type": "qa_pair", "score": 0.87},
        ],
        "confidence_score": 0.90,
        "token_count": 301,
    },
]

# Returned when no keyword match is found
MOCK_FALLBACK: dict = {
    "answer": (
        "This question isn't covered in the current mock knowledge base. "
        "In production, gpt-4o would retrieve relevant chunks from ChromaDB and generate "
        "a cited answer. Switch MOCK_MODE = False in main.py and add your OPENAI_API_KEY "
        "to .env to enable live retrieval."
    ),
    "sources": [],
    "confidence_score": 0.12,
    "token_count": 0,
}


def match_tutor_question(question: str) -> dict:
    """
    Keyword-match the incoming question against MOCK_QA_PAIRS.
    Returns the matching pair dict, or MOCK_FALLBACK if nothing matches.
    """
    q = question.lower()
    for pair in MOCK_QA_PAIRS:
        if any(kw in q for kw in pair["keywords"]):
            return pair
    return MOCK_FALLBACK


# ─────────────────────────────────────────────────────────────────────────────
# PRE-BOARDING — 3 learning paths  (Feature 2, Step 1)
# ─────────────────────────────────────────────────────────────────────────────

MOCK_PREBOARDING_PLANS: list[dict] = [
    {
        "id": "plan_manufacturing_entry",
        "vertical": "manufacturing",
        "experience_level": "entry",
        "sdr_profile_summary": "No prior SaaS sales experience. Background in manufacturing operations. Strong technical aptitude.",
        "plan_title": "Manufacturing SDR Fast Track — Entry Level",
        "estimated_weeks": 6,
        "weeks": [
            {
                "week": 1,
                "theme": "Salesforce Foundations",
                "trailhead_badges": [
                    "Salesforce Platform Basics",
                    "CRM for Lightning Experience",
                    "Sales Cloud Basics",
                ],
                "focus": "Understand what Salesforce does, why manufacturers buy it, and how to navigate the UI.",
                "daily_goal": "2 Trailhead badges per day. Shadow 2 discovery calls with your Trail Guide.",
            },
            {
                "week": 2,
                "theme": "Manufacturing Vertical Deep Dive",
                "trailhead_badges": [
                    "Manufacturing Cloud Basics",
                    "Configure-Price-Quote (CPQ) for Manufacturing",
                ],
                "focus": "Learn the language of manufacturing buyers: OEE, downtime cost, ERP integration pain.",
                "daily_goal": "Complete CPQ module. Research 5 target manufacturing accounts in your territory.",
            },
            {
                "week": 3,
                "theme": "Discovery & Prospecting",
                "trailhead_badges": [
                    "Prospecting and Preparation",
                    "Discovery Conversations",
                ],
                "focus": "Build your 30-second value prop for manufacturing ops leaders. Practice MEDDIC on mock calls.",
                "daily_goal": "15 minutes of call recordings via Gong. 30 cold call attempts with manager present.",
            },
            {
                "week": 4,
                "theme": "Objection Handling",
                "trailhead_badges": ["Objection Handling Fundamentals"],
                "focus": "Manufacturing-specific objections: 'We use SAP', 'ERP handles that', 'Our IT won't allow it'.",
                "daily_goal": "Role-play each objection 5 times with Trail Guide. Write your objection handling script.",
            },
            {
                "week": 5,
                "theme": "Pipeline Building",
                "trailhead_badges": [
                    "Pipeline Management",
                    "Salesforce Reports and Dashboards",
                ],
                "focus": "Build first real pipeline. Target: 3 qualified opportunities logged in Salesforce by end of week.",
                "daily_goal": "50 outreach attempts. Log all activity in Salesforce same-day.",
            },
            {
                "week": 6,
                "theme": "Certification & Ramp",
                "trailhead_badges": ["Salesforce Certified Associate (exam prep)"],
                "focus": "Certification exam + presentation to sales leadership. First solo quota week.",
                "daily_goal": "2 hours exam prep. Present pipeline review to manager on Friday.",
            },
        ],
        "manager_notes": "This plan front-loads vertical knowledge because manufacturing buyers will test technical credibility immediately. Do not rush Week 2.",
    },
    {
        "id": "plan_healthcare_mid",
        "vertical": "healthcare",
        "experience_level": "mid",
        "sdr_profile_summary": "2 years SaaS SDR experience at a health-tech startup. Familiar with HIPAA basics. Strong email game, weaker on phones.",
        "plan_title": "Healthcare SDR Accelerator — Mid Level",
        "estimated_weeks": 4,
        "weeks": [
            {
                "week": 1,
                "theme": "Healthcare Compliance & Salesforce Health Cloud",
                "trailhead_badges": [
                    "Health Cloud Basics",
                    "HIPAA Compliance for Salesforce",
                ],
                "focus": "Understand what healthcare buyers care about: patient outcomes, revenue cycle, staff efficiency. Learn what you can and cannot say under HIPAA.",
                "daily_goal": "Complete Health Cloud module. Shadow 1 AE demo with a hospital system.",
            },
            {
                "week": 2,
                "theme": "Revenue Cycle & Clinical Stakeholder Mapping",
                "trailhead_badges": ["Healthcare Revenue Cycle", "Stakeholder Mapping"],
                "focus": "Map the healthcare buying committee: CMO, CNO, CFO, CIO, and department heads all have veto power.",
                "daily_goal": "Build a stakeholder map for 3 target hospital accounts. Identify your champion profile for each.",
            },
            {
                "week": 3,
                "theme": "Outbound Execution",
                "trailhead_badges": ["Outbound Prospecting Excellence"],
                "focus": "Focus on phone skills — identified as the development area. 60 dials per day. Use the 'patient outcome' opener.",
                "daily_goal": "60 dials. Log all activity. Manager listens to 10 calls and provides same-day feedback.",
            },
            {
                "week": 4,
                "theme": "Pipeline Review & Certification",
                "trailhead_badges": ["Salesforce Certified Associate"],
                "focus": "Present 5 qualified opportunities to manager. First week at partial quota.",
                "daily_goal": "Pipeline review on Wednesday. Certification exam on Friday.",
            },
        ],
        "manager_notes": "Strong written skills — lean into personalized email sequences. Phone coaching is the priority intervention in Week 3.",
    },
    {
        "id": "plan_tech_senior",
        "vertical": "technology",
        "experience_level": "senior",
        "sdr_profile_summary": "5 years enterprise SaaS experience at Outreach and Gong. Deep knowledge of revenue operations. Ready to carry a full enterprise book.",
        "plan_title": "Enterprise Tech SDR — Senior Onboarding",
        "estimated_weeks": 3,
        "weeks": [
            {
                "week": 1,
                "theme": "Salesforce Product Depth & Competitive Landscape",
                "trailhead_badges": [
                    "Salesforce Platform Advanced",
                    "Competitive Positioning",
                ],
                "focus": "Learn how Salesforce differentiates vs. HubSpot, Microsoft Dynamics, and custom builds in tech accounts. Master the integration narrative.",
                "daily_goal": "Shadow 2 enterprise AE calls. Map 5 strategic accounts in your territory.",
            },
            {
                "week": 2,
                "theme": "Multi-Threading & Executive Selling",
                "trailhead_badges": [
                    "Executive Selling",
                    "Multi-Threading in Enterprise Deals",
                ],
                "focus": "Tech CFOs and CTOs are the primary buyers. Build a repeatable C-suite outreach motion. Multi-thread every account from day one.",
                "daily_goal": "Outreach 20 accounts with 3-thread minimum (CRO + CFO + VP RevOps). Present outreach strategy to manager.",
            },
            {
                "week": 3,
                "theme": "Full Quota & Pipeline Review",
                "trailhead_badges": [
                    "Salesforce Certified Sales Cloud Consultant (exam prep)"
                ],
                "focus": "First week at full quota. Pipeline review with VP of Sales on Thursday.",
                "daily_goal": "Full outreach motion. 5 qualified opps minimum by end of week.",
            },
        ],
        "manager_notes": "Skip the basics — this rep needs Salesforce product depth and competitive positioning, not SDR fundamentals. Move fast.",
    },
]


def get_preboarding_plan(vertical: str = "", experience_level: str = "") -> dict:
    """Return the best-matching mock preboarding plan by vertical and experience_level."""
    v, e = vertical.lower(), experience_level.lower()
    for plan in MOCK_PREBOARDING_PLANS:
        if plan["vertical"] in v and plan["experience_level"] in e:
            return plan
    # Fallback: return first plan
    return MOCK_PREBOARDING_PLANS[0]


# ─────────────────────────────────────────────────────────────────────────────
# OFFBOARDING KT — 2 handoff documents  (Feature 3)
# ─────────────────────────────────────────────────────────────────────────────

MOCK_HANDOFF_DOCS: list[dict] = [
    {
        "id": "handoff_tech_midmarket",
        "departing_rep": "Jordan Lee",
        "territory": "AMER West — Mid-Market Tech",
        "tenure_months": 18,
        "departure_reason": "Promoted to AE",
        "summary": "Strong pipeline, 2 deals in late stage, 1 at-risk account needing immediate re-engagement.",
        "key_accounts": [
            {
                "company": "Veritas Analytics",
                "stage": "Proposal Sent",
                "deal_size_usd": 48000,
                "champion": "Priya Nair (VP RevOps)",
                "economic_buyer": "CFO Marcus Webb — engaged once, needs a second touch",
                "next_action": "Follow up on proposal by EOW. Marcus goes on vacation 5/15.",
                "risk": "Competitor (HubSpot) is also in final consideration.",
                "notes": "Priya is very responsive on LinkedIn. Do NOT call the main line — receptionist screens aggressively.",
            },
            {
                "company": "Crestline Software",
                "stage": "Discovery Complete",
                "deal_size_usd": 72000,
                "champion": "David Cho (Director of Sales Ops)",
                "economic_buyer": "CRO has not been introduced yet — David is gating access",
                "next_action": "Ask David directly: 'What would need to be true for you to set up a 30-minute call with your CRO?'",
                "risk": "Low urgency — no fiscal year end pressure until Q4",
                "notes": "David responds to data. Send the RevOps ROI calculator before the next touch.",
            },
            {
                "company": "Apex Platforms",
                "stage": "Prospecting — At Risk",
                "deal_size_usd": 120000,
                "champion": "None identified",
                "economic_buyer": "Unknown",
                "next_action": "Re-engage IT Director Sara Kim who clicked email 3x but never responded.",
                "risk": "HIGH — account has gone cold for 6 weeks. Re-engage or recycle.",
                "notes": "Sara is active on LinkedIn. Try a personalized video voicemail.",
            },
        ],
        "territory_insights": [
            "Mid-market tech buyers in AMER West are budget-approving in March and September — push hard in those windows.",
            "Integration narrative resonates most: 'Salesforce connects your stack' outperforms 'Salesforce replaces your CRM'.",
            "Decision cycle is 45–60 days average. Do not go to proposal before EB intro.",
        ],
        "lessons_learned": [
            "I wasted 3 months on Apex because I never got to the EB. Don't repeat that.",
            "Priya at Veritas responds within 2 hours if you message at 8am PT. Call her, don't email.",
            "The RevOps ROI calculator closes more discovery meetings than any other piece of content in this territory.",
        ],
        "approved": False,
        "approval_status": "pending_dual_approval",
    },
    {
        "id": "handoff_healthcare_enterprise",
        "departing_rep": "Alex Moreno",
        "territory": "AMER Southeast — Enterprise Healthcare",
        "tenure_months": 24,
        "departure_reason": "Departing company",
        "summary": "Large territory with 2 strategic accounts in active evaluation. Strong relationships with 3 health system CIOs.",
        "key_accounts": [
            {
                "company": "Piedmont Health System",
                "stage": "Technical Evaluation",
                "deal_size_usd": 340000,
                "champion": "CIO Robert Tatum — very bought in",
                "economic_buyer": "CFO is the blocker — worried about implementation timeline",
                "next_action": "Bring in Solutions Engineer to address CFO's timeline concern directly. Do this before 5/30.",
                "risk": "MEDIUM — CFO concern is real but addressable with our 90-day deployment data.",
                "notes": "Robert plays golf with our VP of Sales — use that relationship if needed. Do not CC procurement on emails.",
            },
            {
                "company": "Coastal Medical Group",
                "stage": "Initial Discovery",
                "deal_size_usd": 95000,
                "champion": "VP of Operations Dana Reyes",
                "economic_buyer": "CEO not yet engaged",
                "next_action": "Ask Dana to set up an executive briefing with the CEO. Use the '30-minute ROI review' framing.",
                "risk": "LOW — early stage, no competitor present yet",
                "notes": "Dana responds only to phone calls, not email. She's in the office 7am–3pm EST.",
            },
        ],
        "territory_insights": [
            "Southeast healthcare systems are 12–18 month buying cycles. Plant seeds early, stay patient.",
            "Clinical outcome data closes enterprise health system deals. Get the case studies from Marketing.",
            "HIPAA BAA negotiation always adds 4–6 weeks. Loop in Legal before the final proposal.",
        ],
        "lessons_learned": [
            "The biggest mistake I made early on was treating healthcare IT like regular enterprise IT. It's completely different — patient safety language gets attention, ROI language gets dismissed.",
            "Robert at Piedmont would have walked away if I hadn't escalated to the VP relationship. Know when to pull in the cavalry.",
            "Always confirm your champion has executive presence before you close. Dana talks a big game but CFO doesn't know who she is.",
        ],
        "approved": False,
        "approval_status": "pending_dual_approval",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# COACHING NOTES — 3 notes with scores  (Feature 4, Step 10)
# ─────────────────────────────────────────────────────────────────────────────

MOCK_COACHING_NOTES: list[dict] = [
    {
        "id": "note_strong_call",
        "call_quality": "strong",
        "sdr_name": "Taylor Nguyen",
        "prospect": "VP of Sales, Fintech startup (~200 employees)",
        "outcome": "Meeting booked for next Tuesday",
        "duration_minutes": 7,
        "overall_score": 88,
        "score_breakdown": {"opening": 18, "discovery": 23, "objection_handling": 26, "close": 21},
        "what_worked": [
            "Opened with a specific financial metric (revenue close cycle) rather than a product feature — the prospect engaged immediately.",
            "Used silence effectively after the discovery question. Let the prospect talk for 90 seconds uninterrupted — uncovered a real pain point (end-of-quarter reporting chaos).",
            "Handled 'we already use HubSpot' gracefully by asking 'What would need to be true for HubSpot to handle your Q4 close?' — prospect couldn't answer, which exposed the gap.",
            "Closed with two specific time slots instead of 'does next week work?' — booked the meeting in 20 seconds.",
        ],
        "what_to_improve": [
            "The value prop at 2:15 was slightly generic ('Salesforce helps sales teams perform'). Tie it to fintech specifically — they care about revenue velocity, not general productivity.",
        ],
        "language_alternatives": [
            "Instead of: 'Salesforce helps sales teams perform better' → Use: 'Fintech teams using Salesforce close their books 3 days faster on average — that's 36 extra days per year your finance team isn't firefighting.'",
            "Instead of: 'Can we find a time next week?' → Use: 'I have Tuesday at 2pm or Thursday at 9am — which works better for a 20-minute look at how this plays out for your team?'",
        ],
        "approved": False,
        "zero_edit_candidate": True,
    },
    {
        "id": "note_weak_call",
        "call_quality": "weak",
        "sdr_name": "Casey Park",
        "prospect": "Director of IT, Manufacturing company (~500 employees)",
        "outcome": "Prospect hung up at 2:30",
        "duration_minutes": 2,
        "overall_score": 31,
        "score_breakdown": {"opening": 5, "discovery": 6, "objection_handling": 12, "close": 8},
        "what_worked": [
            "Got past the gatekeeper — that's a real skill. Note how you mirrored the gatekeeper's tone.",
        ],
        "what_to_improve": [
            "Opened with 'Hi, how are you today?' — this is the single most common reason manufacturing buyers disengage. They interpret it as a time-wasting courtesy.",
            "When the prospect said 'we're happy with our current setup,' the response was 'Oh okay, what are you using?' — this is a dead end. Prospects don't want to justify their current setup to a stranger.",
            "No discovery question was asked in the 2:30 before the hang-up. Every call needs a question that makes the prospect think, not answer.",
            "Feature-dumped Salesforce Manufacturing Cloud for 45 seconds before the prospect had expressed any interest. Lead with their pain, not our features.",
        ],
        "language_alternatives": [
            "Instead of: 'Hi, how are you today? I'm calling from Salesforce about...' → Use: 'Hi [Name], this is Casey from Salesforce. We just finished helping [Competitor Name] cut their production scheduling cycle by 30% — is that kind of efficiency gain on your team's radar this year?'",
            "Instead of: 'Oh okay, what are you using?' after the brush-off → Use: 'That makes sense — most manufacturers I talk to felt the same way until their Q3 close showed gaps in visibility. Can I ask what your current setup looks like for production tracking?'",
        ],
        "approved": False,
        "zero_edit_candidate": False,
    },
    {
        "id": "note_average_call",
        "call_quality": "average",
        "sdr_name": "Morgan Diaz",
        "prospect": "VP of Revenue Operations, SaaS company (~1,200 employees)",
        "outcome": "Requested email follow-up, no meeting booked",
        "duration_minutes": 5,
        "overall_score": 59,
        "score_breakdown": {"opening": 16, "discovery": 15, "objection_handling": 16, "close": 12},
        "what_worked": [
            "Strong opener — led with a specific peer company outcome (Gong case study) that was highly relevant to a RevOps leader.",
            "Identified that the prospect has a manual reporting problem — that's a real pain point worth pursuing.",
            "Kept a professional, confident tone throughout.",
        ],
        "what_to_improve": [
            "When the prospect said 'send me an email,' accepted that at face value and ended the call. A stronger response would have extracted one more piece of information before agreeing to send.",
            "The meeting ask came too early (at 1:45) before pain was fully established. The prospect didn't yet understand what they'd be meeting about.",
            "No specific time slots offered when asking for the meeting — 'does next week work?' is too open-ended and invites a no.",
        ],
        "language_alternatives": [
            "Instead of: 'Sure, I'll send you an email — what's the best address?' → Use: 'Happy to send something over. So I can make it specific to your situation — is the manual reporting issue something that's blocking your team right now, or more of a Q3 priority?'",
            "Instead of: 'Would it make sense to connect next week?' → Use: 'I have two 20-minute slots open — Tuesday at 3pm or Thursday at 10am Pacific. Which works better to walk through the reporting automation piece?'",
        ],
        "approved": False,
        "zero_edit_candidate": False,
    },
]


def get_coaching_note(quality: str = "strong") -> dict:
    """Return a mock coaching note by call quality (strong | weak | average)."""
    for note in MOCK_COACHING_NOTES:
        if note["call_quality"] == quality:
            return note
    return MOCK_COACHING_NOTES[0]
