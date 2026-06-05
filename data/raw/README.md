# `data/raw/`

Seed inputs for the SDR onboarding workflow. Read-only — skills and automations consume these and write derived rows under `data/working/`.

## `sdr_profiles.csv`

Ten incoming Sales Development Reps to be matched with AE mentors. Each row describes one new hire's territory, vertical specialization, experience level, and the role they're transitioning from.

| Column | Type | Notes |
| --- | --- | --- |
| `hire_id` | string | Primary key, `HIRE-001` … `HIRE-010` |
| `name` | string | Full name |
| `territory` | enum | `AMER-West`, `AMER-East`, `EMEA`, `APAC` |
| `vertical` | enum | `fintech`, `healthcare`, `retail`, `SaaS` |
| `experience_level` | enum | `entry`, `mid`, `senior` |
| `prior_role` | string | Free-text description of background |

## `ae_profiles.csv`

Fifteen Account Executives available as mentors. Used by the matching step to find a strong territory + vertical pairing for each SDR, weighted by satisfaction, capacity, and mentorship history.

| Column | Type | Notes |
| --- | --- | --- |
| `ae_id` | string | Primary key, `AE-001` … `AE-015` |
| `name` | string | Full name |
| `territory` | enum | Same set as SDR territories |
| `vertical` | enum | Same set as SDR verticals |
| `tenure_years` | int | 3–10 |
| `satisfaction_score` | float | 3.5–4.8, internal pulse-survey score |
| `mentorship_hours_per_week` | int | 1–5, weekly capacity for mentoring |
| `prior_mentees` | int | 0–12, count of SDRs previously mentored |
