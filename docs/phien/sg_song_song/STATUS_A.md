Mode: SG_SONG_SONG person A
LOCK: LEAD session_01TGThn8FotZk5dp89pKN66o 2026-11-13T12:54Z
STATUS: RUNNING
BASE: 98709f1f374368c65ee2833467715fd933dc84f6   SNAPSHOT: n/a for person A (no generator item; leads B/C hold the snapshot)
Branch claude/sg-a starts at ba4b207 = BASE + 2 doc-only commits (SG_SONG_SONG.md, claude__sg-sua.md) so workers read the current 2.9/2.10.

## Items
| Item | State | Round | Start | End | Coder session | Checker session | Tests |
|---|---|---|---|---|---|---|---|
| SG-1 (C3) | CODING | 0 | ffb6ce2 | | session_01TGThn7GRLE7ML1TDfW53iL | | |
| SG-3 (C2) | TODO | 0 | | | | | |
| SG-4 (M3) | TODO | 0 | | | | | |
| SG-10 (M2) | TODO | 0 | | | | | |
| SG-11a (M6, M7, L1, L4, L5) | TODO | 0 | | | | | |

## Fix lists

## Decisions
- D-A1: Fable's report artifact is not readable from this account (artifact not found). Per 2.1, red tests come from the spec text (SOAT_GIAO_DIEN_KE_HOACH.md §3) and the code.
- D-A2: claude/sg-a branched from origin/claude/forms-gop tip (ba4b207), not BASE 98709f1: the two extra commits only touch docs/ke_hoach/SG_SONG_SONG.md and docs/phien/claude__sg-sua.md. Diffs and checker START use item Start hashes, so nothing else changes.
- D-A3: SG-11 scope for person A = M6, M7, L1, L4, L5 (+ one-line consistency rules, glossary list to docs/). M4 belongs to person B (SG-11b).

## For Truong

## Log
2026-11-13T12:54Z LEAD session_01TGThn8FotZk5dp89pKN66o SETUP lead-is-opus ba4b207
2026-11-13T12:54Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-1 CODING coder=session_01TGThn7GRLE7ML1TDfW53iL ffb6ce2
2026-11-13T13:04Z CODER session_01TGThn7GRLE7ML1TDfW53iL SG-1 READY 9934af2 red:5 of 8 new tests failed before fix (no tested_scores arg, no code in run/health) mutation:zero-score condition replaced by False -> 3 tests fail, restored
