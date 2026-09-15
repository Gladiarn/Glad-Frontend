# Glad Frontend

A [Claude Code / agent skill](https://github.com/vercel-labs/skills) that makes frontend UI **backend-ready by construction**.

One rule: no hardcoded display data anywhere. Every dynamic list, table, or detail view flows through a hook/store backed by a repository interface, with a mock implementation that behaves like a real API (real latency, real failure, real loading/error/empty states) and a real implementation that will replace it later — swapping one for the other touches exactly one binding, never the UI.

## Scope

This skill owns **data architecture only**. It has no opinion on visual style, layout, typography, or color — that's the job of whichever design skill is active alongside it ([`frontend-design`](https://github.com/anthropics/skills), [`impeccable`](https://github.com/pbakaus/impeccable), or anything else). Keeping that boundary sharp means this skill stays useful no matter which design skill you pair it with.

## Install

```bash
npx skills add https://github.com/Gladiarn/Glad-Frontend --skill glad-frontend
```

## Why

Most frontend work hardcodes strings/arrays straight into JSX. That works today and creates real work later: when the backend ships, someone has to find every literal, understand what it stood in for, and rebuild the data flow without breaking the layout — and that rebuild is exactly when corners get cut. A mock-first component never has this problem, because the UI was never coupled to *where* the data came from, only to its *shape*.

See [`skills/glad-frontend/SKILL.md`](skills/glad-frontend/SKILL.md) for the full pattern, checklist, and anti-patterns table.

## License

MIT — see [LICENSE](LICENSE).
