---
name: frontend-ready
description: Build distinctive, non-templated frontend UI that is fully backend-ready from day one — no hardcoded display data anywhere, everything flows through state backed by a swappable mock/real data layer. Use whenever the user asks to build a new page, component, table, list, dashboard, or form before a backend/API exists, wants the frontend to be "ready to plug in the backend later," asks for a design that doesn't look generic/templated/AI-generated, or is scaffolding UI ahead of API availability.
---

# Frontend Ready

Two requirements govern every frontend build under this skill, and neither is optional:

1. **The design must be distinctive**, not a templated default.
2. **The frontend must be backend-ready by construction** — swapping mock data for a real API later touches one file, never the UI.

Most frontend work satisfies neither by default: it hardcodes strings/arrays straight into JSX, and it converges on the same handful of AI-generated-looking layouts. This skill exists to prevent both failure modes at once, because they compound — a component wired to hardcoded data has to be *rebuilt*, not *reconnected*, when the backend shows up, and that rebuild is exactly when corners get cut and the design regresses to generic.

## Why mock-first, not hardcoded

A hardcoded table (`<tr><td>Alice</td>...` written directly in JSX) works today and creates real work tomorrow: someone has to find every literal, understand what it was standing in for, and rebuild the data flow while also not breaking the layout. A mock-first component never has this problem, because the UI was never coupled to where the data came from — only to its shape.

## The pattern: repository interface, two implementations

This mirrors the Repository Pattern in `backend-patterns` — use the same vocabulary so frontend and backend stay consistent when the same person (or you) builds both.

1. **Define the data shape first**, as a type, before writing any UI:
   ```typescript
   interface Market {
     id: string
     name: string
     status: 'active' | 'closed'
     volume: number
   }
   ```

2. **Define a repository interface** — the contract the UI will always talk to, regardless of what's behind it:
   ```typescript
   interface MarketRepository {
     findAll(filters?: MarketFilters): Promise<Market[]>
     findById(id: string): Promise<Market | null>
   }
   ```

3. **Implement it twice.** Mock now, real later — same shape, same async contract, so swapping is a binding change, not a rewrite:
   ```typescript
   class MockMarketRepository implements MarketRepository {
     async findAll(filters?: MarketFilters): Promise<Market[]> {
       await simulateLatency() // see "Simulate reality" below
       return mockMarkets.filter(/* apply filters */)
     }
     async findById(id: string) {
       await simulateLatency()
       return mockMarkets.find(m => m.id === id) ?? null
     }
   }

   class ApiMarketRepository implements MarketRepository {
     async findAll(filters?: MarketFilters): Promise<Market[]> {
       const res = await fetch(`/api/markets?${toQuery(filters)}`)
       if (!res.ok) throw new ApiError(res.status, 'Failed to load markets')
       return res.json()
     }
     async findById(id: string) {
       const res = await fetch(`/api/markets/${id}`)
       if (res.status === 404) return null
       if (!res.ok) throw new ApiError(res.status, 'Failed to load market')
       return res.json()
     }
   }
   ```

4. **Bind one implementation in exactly one place** — an env flag, a config module, or dependency injection at the app root. Never let a component import `MockMarketRepository` or `ApiMarketRepository` directly.
   ```typescript
   export const marketRepository: MarketRepository =
     process.env.NEXT_PUBLIC_USE_MOCKS === 'true'
       ? new MockMarketRepository()
       : new ApiMarketRepository()
   ```

5. **Components and hooks consume the interface, never the implementation:**
   ```typescript
   function useMarkets(filters?: MarketFilters) {
     const [markets, setMarkets] = useState<Market[]>([])
     const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading')

     useEffect(() => {
       setState('loading')
       marketRepository.findAll(filters)
         .then(data => { setMarkets(data); setState('ready') })
         .catch(() => setState('error'))
     }, [JSON.stringify(filters)])

     return { markets, state }
   }
   ```
   The table component that renders `markets` never knows or cares whether they came from a mock array or a live fetch. When the backend ships, flip the env flag. Nothing above the repository boundary changes.

## Simulate reality in the mock layer

A mock that resolves instantly and never fails teaches the UI to assume APIs always do too — that assumption breaks in production. The mock implementation must:

- **Add latency** (150–600ms, randomized) so loading states actually get exercised and designed, not bolted on later.
- **Occasionally fail** (configurable rate, default off but easy to flip on) so error states are real UI, not an afterthought.
- **Return realistic volume and content** — not `"Item 1"`, `"Item 2"`. Use plausible names, varied string lengths, edge cases (empty state, one item, 200 items) so layout decisions are grounded in what real content actually looks like. Lorem-ipsum-driven layouts are a top source of the generic look this skill also exists to avoid — see below.

Every data-bound component must handle three states because of this: loading, error, and empty (zero results is not the same bug as "still loading"). If a component only handles the success case, it is not done.

## Never hardcode — checklist before calling UI work finished

- [ ] No array/object literal in a component file stands in for data that will come from a backend (mock data lives in a dedicated `mocks/` or `fixtures/` module, never inline in the component)
- [ ] Every dynamic list, table, or detail view reads from a hook/store backed by a repository, not an imported mock file directly
- [ ] Loading, error, and empty states are implemented and visually designed, not just `if (loading) return null`
- [ ] The mock repository implements the *same interface* the real one will — check this by asking "if I swapped the binding right now, would any component need to change?" The answer must be no.
- [ ] Config/copy that is genuinely static (labels, nav items, legal text) is fine to hardcode — this rule is about data that originates from a backend, not literally everything

## Distinctive, non-generic design

Backend-readiness governs data flow; it says nothing about whether the result looks distinctive or like every other AI-generated page. For that:

- **Before designing**, consult the `frontend-design` skill for the specific tells of generic AI-generated output (default color/type combinations, the SaaS-card kit, eyebrow labels, arrow-suffixed buttons) and its two-pass plan-then-build process. Ground the visual direction in this project's actual subject matter, not a safe default.
- **If `impeccable` is available and the task warrants its deeper workflow** (a full page or surface, not a small tweak), consult it for the structured critique/polish/audit commands.
- **Before finishing**, consult `web-design-guidelines` and apply its accessibility, focus-state, and form rules — a distinctive design that fails basic accessibility is not done either.
- Design against the realistic mock content from the data layer above, not lorem ipsum — real-feeling data surfaces real layout problems (text overflow, varying lengths, empty states) that placeholder text hides.

## Anti-patterns

| Pattern | Why it fails |
|---|---|
| `<td>{"Alice"}</td>` hardcoded in JSX | Has to be found and rebuilt, not reconnected, when the backend arrives |
| Component imports `mockUsers` array directly | Couples UI to the mock; swapping to a real API means editing every component instead of one binding |
| Mock resolves synchronously, never errors | Loading/error states never get built, then ship broken when the real API is slow or fails |
| Lorem ipsum / `"Item 1"`, `"Item 2"` placeholder content | Hides real layout problems; produces designs that break on real content later |
| Repository interface skipped, `fetch()` called straight from mock mode with a hardcoded mock response inline | No real swap point exists — "temporary" mock logic ends up scattered through the codebase |
