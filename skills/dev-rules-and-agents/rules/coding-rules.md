# Coding Rules (general / project-agnostic)

Universal engineering rules. Portable across any project — drop the relevant lines into a
project's `CLAUDE.md` / `AGENTS.md` / `.cursor/rules`, or reference this file from a prompt.

## Working style
- Assume full execution of the task. Don't ask "should I continue?" — continue until done or blocked.
- Don't ask for clarification when context can be inferred from the request or recent interactions.
- Be precise and token-efficient; give the best answer, not the longest.
- Reuse before writing: if logic already exists elsewhere, refactor and reuse it instead of adding a copy.
- State the shell/OS up front and use its native syntax (e.g. PowerShell on Windows: `$null`, `$env:VAR`, backtick line-continuation).

## Code quality
- Files stay small and single-responsibility (target ≤300 lines); split concerns across files.
- SOLID + KISS. Refactor and remove dead code as you go. Update docs and tests with the change.
- TypeScript strict mode; never use `any` — use specific types or generics.
- React: functional components + hooks. No class components.
- Atomic Design folders (atoms / molecules / organisms / templates / pages).
- No inline styles. No Tailwind. Use CSS Modules, shadcn/ui, or styled-components.
- UI/logic separation: no business logic, parsing, transformation, or data fetching inside UI
  components — move it to hooks or service files. Lift state to Context/store after >2 prop levels.

## Safety
- Never reset or drop a database unless explicitly instructed.
- Confirm before any destructive operation (drop, delete, truncate, force-push, overwrite).
- SQL changes: new timestamped `.sql` file, run + validate, paste output as SQL comments, add a
  companion `.md` explaining the change, and always include a rollback. Make scripts idempotent
  (safe to re-run when the table/view/column already exists). Don't repeat table/schema prefixes
  in column names.

## Docs & diagrams
- Put explanations and context in Markdown files, not in chat — link to the file you changed.
- README.md per directory. Consistent naming, relative Markdown links, lists for readability.
- Diagrams: provide both a rendered view (when supported) and the raw Mermaid syntax.
