# Dristhi: 80 → 95 Hackathon Upgrade Plan

This document compiles a realistic, high‑impact plan to raise the GenAI Exchange Hackathon score from ~80/100 to ~95/100. It contains scope, estimates, acceptance criteria, and suggested sequencing tailored to Dristhi’s current codebase (FastAPI + React + FAISS + provider‑agnostic AI).

---

## Summary and score delta

- Target lift in 2–4 days of focused work: +12–15 points
  - Technical Merit: +3.5–4
  - User Experience: +1.0–1.5
  - Alignment with Cause: +1.5–2
  - Innovation & Creativity: +2.5–3
  - Market Feasibility: +2–3

Key themes: add reliability evidence (E2E + health), enforce an advice template, minimal RAG for personalization, India‑specific feeds, micro‑delight (benchmark, streaks), and crisp GTM story.

---

## 1) Technical Merit (40%) — Target +4

Already strong: modular FastAPI, FAISS memory, provider‑agnostic AI, clean frontend & code‑splitting.

Gaps: shallow tests, weak RAG integration, limited health/observability.

### Tasks

- E2E happy‑path test (Create goal → Ask AI → Start learning path)
  - Est: 0.5–1 day
  - Tooling: pytest (API) or Playwright (UI)
  - Acceptance:
    - Test passes locally, asserts non‑500 responses and expected JSON shape.
    - Verifies advice present and learning path “started_at” updates.

- Health dashboard endpoint (service readiness)
  - Est: 2–4 hours
  - Acceptance:
    - GET /api/v1/healthz returns: { db: ok, ai: {available, model}, faiss: {ok, index_count}, version, uptime }.
    - Returns 200 with truthful flags even if AI unavailable.

- Mini RAG pipeline (retrieve → stuff → answer)
  - Est: 1 day
  - Scope: use FAISS to fetch top 3 context snippets; include in a fixed prompt; return markdown in template.
  - Acceptance:
    - Response includes a “Context used” footnote (ids/titles), and safe fallback when no results.

- Observability basics
  - Est: 2–3 hours
  - Acceptance:
    - Correlation‑ID middleware; structured logs; /metrics with request_count, latency, error_count.

- Reliability guardrails
  - Est: 1–2 hours
  - Acceptance:
    - AI calls have explicit timeouts; fallback JSON preserved; no hard 500s on AI outages.

---

## 2) User Experience (10%) — Target +1.5

Already strong: dark mode; clear CTAs; dashboard; Career page with learning paths; Reality Check banner.

Gaps: onboarding light; advice formatting inconsistent.

### Tasks

- Onboarding wizard (branch, year, interests, target role, location)
  - Est: 3–5 hours
  - Acceptance:
    - 3–4 step flow; saves to user.preferences; used in recommendations.

- Enforce AI advice template (server‑side)
  - Est: 3–4 hours
  - Template sections: Overview; Next 3 Steps (checklist); 3 Resources (title + link); Risks/Watchouts
  - Acceptance:
    - Even on fallback, response respects the template (markdown).

- Roadmap export/share
  - Est: 0.5–1 day
  - Acceptance:
    - Print‑to‑PDF stylesheet produces clean one‑page export; shareable read‑only link.

- UX polish
  - Est: 2–3 hours
  - Acceptance:
    - Skeleton loaders; better empty states; “Why this skill?” tooltips; keyboard focus & aria labels.

---

## 3) Alignment with Cause (15%) — Target +2

Already good: India‑focused Reality Check; education‑aware roadmap.

Gaps: India‑specific feeds in‑app; curated starter packs.

### Tasks

- Internship/Hackathon feed (seeded JSON)
  - Est: 3–5 hours
  - Acceptance:
    - “Opportunities” section lists 10–20 entries; filters by location/remote; external links open in new tab.

- Local learning “Starter Packs” per skill
  - Est: 3–4 hours
  - Acceptance:
    - Each core skill shows ~5 curated NPTEL/YouTube/GeeksforGeeks links.

---

## 4) Innovation & Creativity (20%) — Target +3

Already good: Reality Check; Wellness lens; memory scaffolding.

Gaps: peer benchmarking; daily delight.

### Tasks

- Peer benchmarking (mock)
  - Est: 0.5 day
  - Acceptance:
    - Simple seeded percentile per branch/year; displays “Top X% in Python” badge; clearly labeled as sample cohort.

- Gamification nudge
  - Est: 3–5 hours
  - Acceptance:
    - Daily streak counter; 1–2 badges; celebratory toast on unlock; persistent across refresh.

- Reality Check Plus chart
  - Est: 3–5 hours
  - Acceptance:
    - Static chart (salary vs cost vs demand) using heuristic values; labeled axes; fits on one card.

---

## 5) Market Feasibility (15%) — Target +3

Already clear ICP (engineering students). Gaps: monetization + GTM.

### Tasks

- Freemium mock
  - Est: 2–3 hours
  - Acceptance:
    - Pricing modal: Free (roadmap) vs Premium (mentor review, export analytics, personalized packs).

- Campus GTM plan (+ “College Mode” flag)
  - Est: 2–3 hours
  - Acceptance:
    - Config flag preloads branch resources; slide describing outreach (societies, placement cells, 50‑college pilot).

- Open‑source edge
  - Est: 1–2 hours
  - Acceptance:
    - README notes on localizable resource JSON; indicate language roadmap.

---

## Additional improvements (Architecture/AI/Frontend)

- API contracts & compatibility: keep /api/v1 stable; add compatibility stubs to avoid 404s in demos.
- Feature flags: env toggles for RAG, benchmarking, feeds to de‑risk demos.
- Background jobs: Celery beat to refresh feeds daily; precompute benchmarking snapshot.
- Streaming: SSE support for chat to improve perceived intelligence.
- AI context: rerank by semantic + recency; trim context length; enforce template in all responses.
- Security & Rate limiting: slowapi caps on public endpoints; input validation (Pydantic models already in place).
- Performance & A11y: prefetch routes; lazy load heavy charts; aria‑live regions; focus management in modals.
- Data indexes: user_id and created_at on main tables; FKs used in joins.

---

## Suggested 3–4 day sprint plan

- Day 1
  - Onboarding wizard
  - AI advice template enforcement
  - Health dashboard endpoint
  - E2E happy‑path test

- Day 2
  - Mini RAG pipeline
  - Roadmap PDF/share
  - Internship/Hackathon feed (seed JSON)
  - Peer benchmarking mock

- Day 3
  - Gamification (streaks/badges)
  - Reality Check Plus chart
  - Observability basics (/metrics, request_id)
  - A11y + skeletons

- Day 4 (polish)
  - Test pass; UX papercuts; seed validation
  - Tighten demo script; record 60–90s fallback screen capture

---

## Acceptance checklists (for demo readiness)

- Health
  - [ ] /api/v1/healthz returns ai/db/faiss/version/uptime; never 500 under AI outage
- Advice
  - [ ] Markdown template always present (Overview, Next 3, 3 Resources, Risks)
  - [ ] Fallback returns same structure if AI down
- RAG
  - [ ] Response references 1–3 context items or indicates no context used
  - [ ] Timeouts safe; no hard 500s
- Onboarding
  - [ ] Preferences saved; used by recommendations
- Export
  - [ ] One‑page printable roadmap; shareable token link
- Feed
  - [ ] 10–20 opportunities; links open in new tab; simple filters work
- Benchmark
  - [ ] Percentile badge visible; marked as “sample cohort”

---

## Demo script (3–5 minutes)

1) Hook (30s): “Generic advice hurts students; Dristhi gives a personalized roadmap and shows ROI with Reality Check.”
2) Onboarding (20s): capture branch/year/goal; save.
3) Career (60–90s): create/activate goal → AI feedback (templated markdown) → open Learning Path modal (milestones/projects) → start path.
4) Reality Check (30–45s): show ROI + (Plus) chart.
5) Wellness (20–30s): habits today + average mood → consistency story.
6) Differentiators (20–30s): benchmarking badge, PDF export, AI status/health.
7) Close (15–20s): GTM + freemium; India‑first resource packs; campus rollout.

---

## Appendix: Risks & Mitigations

- AI latency/unavailability → timeouts + template fallback; demo mode seeding.
- Data sparsity → preseed one active goal + learning path; curated starter packs.
- Judge network constraints → record a 90s demo video as backup.

---

Last updated: 2025‑10‑02
