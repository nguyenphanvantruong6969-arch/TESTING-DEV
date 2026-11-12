# Brief for a Fable research session: how to improve RB-DA / FA-DAA

> Read `docs/fable/01_PROJECT_CONTEXT.md` first. Written 2026-11-12. English on purpose.
> Role of this session: **research and design partner**, not the coder. Output = a research memo with
> proposals mapped to registry item codes, plus test/simulation plans. Code changes only if Truong asks.

---

## 1. Ground rules (from `CLAUDE.md`, non-negotiable)

- Keep the 8 invariants. Any idea that breaks one must say so explicitly and propose the exception text
  for Truong to decide (as done for D2), never assume it.
- Map every proposal to one registry item (Z1…G5, A13 sub-items, or "new item, outside the registry").
- All numbers are SIMULATED; label every table "SỐ LIỆU MÔ PHỎNG". Never present them as a real survey.
- **Academic integrity:** do not write the report's commentary, interpretation or conclusions. Give
  evidence, options, proofs, references and simulation designs; Truong writes the conclusions.
- Check every citation (authors, year, title) against Crossref/arXiv before relying on it; the project's
  literature list contains known errors. Correct spelling: Gale–Shapley.
- No subagents unless Truong says so. Reply to Truong in Vietnamese; files in English.
- Role (`CLAUDE.md` rule 11, Truong 2026-11-12): Fable researches — reads code and docs, runs simulations
  in `du_lieu_test/` or a scratch folder, writes memos under `docs/fable/`; never edits production code.

## 2. Research goals (priority order)

### G-A. Audit the current mechanism for hidden weaknesses (highest value, needed before real use)
Questions:
1. Does FA-DAA keep stability and strategy-proofness *given medals* with all its wrapper steps: SELECTIVE
   filtering, FREE fallback + rerun, club-closing loop (D3), reserved seats as soft reserve (D6)? Give a proof
   sketch or a counterexample per step, and property tests that would catch a violation.
2. Medal placement is itself a strategic choice. How much can a strategic student gain over the default
   (lazy) placement? Who loses? Does the default (D2) leave lazy students systematically worse off?
3. Integer 0–10 scores (D7) → many ties → more lottery. What score granularity or tie rule reduces lottery
   share without hurting truthfulness or fairness between quiz variants (D11)?
Existing tools: `du_lieu_test/mo_phong_fa_daa.py`, `tests/test_fa_tinh_chat.py`, `fa_vong_doi_cho.py`.

### G-B. Efficiency vs stability
24 % of students in `bo_sach` are in a mutually beneficial swap. Quantify, on FA-DAA data, what Erdil–Ergin
stable improvement cycles (already in measurement mode) recover, who benefits by behaviour type, and whether
it opens manipulation. Compare with alternatives (e.g. efficiency-adjusted DA, Kesten 2010) at the level of
"what would we have to give up". Recommend keep-off / turn-on conditions.

### G-C. Changes over time (owner's main expansion goal; items G1–G5)
1. Late arrivals and capacity decreases: resume DA from stored state (G1). Design a millisecond-level
   incremental method (indexed priority lists + bisect) and state exactly when it equals a full rerun.
2. Withdrawals and capacity increases (G2): vacancy chains vs replay from a checkpoint. Is either provably
   equal to a full rerun? If not, what property is lost?
3. Protecting announced students (G3): soft reserves + a blocking-pair budget; quantify the trade-off
   (simulated: 20 late arrivals demote 32 earlier students on average at capacity ratio 0.8).
4. How this interacts with the append-only adjustment log (`fa_dieu_chinh`) and waitlist invitations.
Relevant literature to verify: dynamic school choice / reassignment (e.g. Pereyra 2013; Dur 2012;
Combe, Tercieux & Terrier 2022; Feigenbaum, Kanoria, Lo & Sethuraman 2020).

### G-D. Capacity is the biggest lever
Simulations say matching seats to demand raises first-choice rate from ~48 % to ~79 % at the same total.
Design the best capacity-suggestion rule for teachers who may only increase seats (`bang_nhu_cau`,
`goi_y_chi_tieu`), robust to students reacting to announced capacities. Include the D1 decision (compensation
credit A/B/C): larger simulation design, incentive analysis, and the exact invariant-2 exception wording if B or C.

### G-E. Generalisation architecture (items Z7, A1–A3, A12)
Propose the plug-in interface for priority functions, choice functions and eligibility rules; an automatic
substitutability / law-of-aggregate-demand checker for new choice functions; and which light sector to pilot
first (DT, NT, KTX or SK) with the minimum item list. Keep invariant 1 (default byte-identical).

### G-F. Scale (items Z4, Z5) — lower priority for the school, required for sector TS
Prove (or refute) that the bisect-based `verify_stability` is equivalent to the original for the two-pass
choice function; derive a correct `max_rounds` bound (sum of list lengths) and the error path when hit.

## 3. Deliverables

1. `docs/fable/03_RESEARCH_MEMO.md` (English, ≤ 400 lines): per goal → finding, evidence (proof sketch,
   counterexample, or simulation table labelled SIMULATED), proposal mapped to an item code, risk to each
   invariant, acceptance test (`kiem_nhan`) in the registry's style.
2. Simulation scripts only under `du_lieu_test/` or a scratch folder, read-only use of the production code.
3. A short Vietnamese summary to Truong: top 3 recommendations, decisions he must make, what to verify.
4. A 3–5 line note of what the AI did, so Truong can add it to the project's AI log himself.

## 4. How to run the Fable session

**Option 1 (recommended): Claude Code on this repository, branch from `claude/forms-gop`.**
Fable reads `CLAUDE.md` automatically and can run the simulations. Suggested effort: `high`
(raise to `xhigh` only for the proof-heavy goal G-A/G-C). Give it one goal per session; long sessions
are fine, but each goal should end with its memo section written.

**Option 2: claude.ai chat (no code execution on the repo).** Upload, in this order:
1. `docs/fable/01_PROJECT_CONTEXT.md`, `docs/fable/02_FABLE_BRIEF.md`
2. `CLAUDE.md`
3. `docs/ke_hoach/BOI_CANH_DU_AN.md`
4. `docs/ke_hoach/FA_DAA_VISION.md`, `docs/ke_hoach/FA_DAA_KE_HOACH.md`
5. `docs/ke_hoach/FA_GAPS_D1_MEMO.md`, `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`
6. Code: `rbda_priority_pipeline.py` (or only the functions in context §2), `fa_daa.py`, `fa_sau_xep.py`,
   `fa_vong_doi_cho.py`, `du_lieu_test/mo_phong_fa_daa.py`
7. Only for G-E: `docs/ke_hoach/SO_DANG_KY_33_MUC.md`
Do not upload `app.db`, real student lists or anything with personal data.

## 5. Ready-to-paste prompts

**Session 1 — mechanism audit (G-A):**
```
Read docs/fable/01_PROJECT_CONTEXT.md and docs/fable/02_FABLE_BRIEF.md, then CLAUDE.md.
Work on goal G-A only. I want to know where FA-DAA could fail stability, truthfulness or fairness
before we use it with real students this semester. For each wrapper step in chay_fa_daa, give a proof
sketch or a smallest counterexample, and the property test that would catch it. Measure how much a
strategic medal placement gains over the default, by behaviour type, with mo_phong_fa_daa.py.
Label all numbers as simulated. Do not change production code. Write the G-A section of
docs/fable/03_RESEARCH_MEMO.md and give me a short Vietnamese summary with the decisions I must make.
```

**Session 2 — changes over time (G-C):**
```
Read the two docs/fable files and CLAUDE.md. Work on goal G-C. Design how the kiosk should handle late
arrivals, withdrawals and capacity changes after results are announced, without breaking the invariants.
For each event type say whether an incremental method provably equals a full rerun, and if not, what is
lost. Propose the protection rule for announced students with a simulated trade-off table. Map every
proposal to G1–G5 with an acceptance test. Verify each citation before using it.
```

**Session 3 — capacity and compensation (G-D):**
```
Read the two docs/fable files, CLAUDE.md and docs/ke_hoach/FA_GAPS_D1_MEMO.md. Work on goal G-D.
Find the best capacity-suggestion rule for teachers who may only add seats, and settle D1 (A, B or C)
with a larger simulation and an incentive analysis. If you recommend B or C, draft the exact exception
text for invariant 2 for me to approve. Do not write report conclusions.
```

## 6. What Fable should NOT do

- Rewrite the DA core, change default results, or edit `run_history`/`match_results` semantics.
- Reintroduce rejected options (decision log, `FA_DAA_VISION.md` §15): free point-splitting, rank-based
  priority, first-come priority, auto-converting FREE clubs to LIMITED, Course Match this term.
- Present simulated numbers as findings about real students, or draft the project report's conclusions.
