# Refactoring Rules — how dedup / consolidation work is done

A durable, improving methodology for refactor + de-duplication sessions. **Reuse it every refactor
session and update it as the methodology grows.** One-liners; keep them tight.

## Safety (don't break the working app)
- **Behavior-preserving by default** — a dedup must produce identical observable output; if it can't, it's not a dedup.
- **Verify equivalence before merging** — quote both implementations, confirm they are byte/algorithm-identical; if they differ, don't merge.
- **Reject the audit when it's wrong** — judgment over blind application. A "duplicate" that touches a tested API, isn't actually equivalent, or has variant drift is not a merge candidate.
- **Preserve intentional divergence via options**, not forked copies.
- **Additive fixes over rewrites** — emit-only-when-present changes can't regress existing output.
- **Never change a tested public API** just to dedup; keep the name/contract.

## Single source of truth
- **Extract shared logic to one util**; callers become **thin delegating wrappers** that keep their names/exports → zero caller churn.
- **Generic over specific** when one algorithm serves multiple shapes (`<T extends { children?: T[] }>`), still fully typed — no `any`.
- **Reuse before writing** — if logic exists, refactor to share it, don't add a copy.
- **Fix latent bugs surfaced while deduping**, but call them out in the commit.

## Proof (done = proven)
- **Gate every change:** type-check clean **+** tests green **+** a real production build green.
- **Type-checkers lie on moves** (incremental cache) — the bundler/build is the real gate for import/path changes; bust the build cache (e.g. `.tsbuildinfo`) when in doubt.
- **Commit per issue**, small + frequent; the message references the item id and states the proof.

## Code quality
- **No `any`** anywhere — generics or specific types.
- **Files ≤300 lines, single responsibility**; split god-files into types/utils/hooks/subcomponents.
- **Barrels for folder moves** so external imports stay stable.

## Token economy
- **Targeted tests per fix; full build + suite batched** every 2–3 fixes / before push.
- **Delegate wide cross-file reads/equivalence checks to a subagent**; apply edits in the main session.

## Coordination
- **Concurrent sessions sync via a shared status file + git** — lock active files, list done/next, commit often so others see progress.
