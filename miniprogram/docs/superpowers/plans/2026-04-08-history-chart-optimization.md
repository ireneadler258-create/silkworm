# History Chart Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the history page chart so the 1h range is always readable, perceived loading is faster, and the UI feels more polished and cohesive.

**Architecture:** Keep the existing uni-app + Vue 3 + TypeScript structure. Implement the change in three focused areas: page state modeling in `src/pages/history/index.vue`, rendering/interaction fixes in `src/components/LineChart.vue`, and non-blocking history readiness behavior in `src/store/device.ts`.

**Tech Stack:** Vue 3 `<script setup>`, TypeScript, uni-app canvas, Pinia-style reactive store

---

## File Map

### Modify
- `src/pages/history/index.vue`
  - Add explicit chart view states and low-data handling
  - Refine chart area layout and coordinated styles
- `src/components/LineChart.vue`
  - Add status-aware rendering and fix point index mapping
  - Improve visual contrast and reduce unnecessary interaction overhead
- `src/store/device.ts`
  - Improve history readiness behavior for page consumption without blocking on cloud sync
  - Keep existing sync flow but expose safer state for UI usage

### Verify
- `docs/superpowers/specs/2026-04-08-history-chart-design.md`
- `package.json` (`npm run type-check`)

---

### Task 1: Add explicit history chart state in the page

**Files:**
- Modify: `src/pages/history/index.vue`
- Reference: `src/store/device.ts:515-519`

- [ ] **Step 1: Add derived state for raw history sufficiency**

Create computed values in `src/pages/history/index.vue` for:
- `rawPointCount`
- `hasRealData`
- `isLowData`
- `chartViewState` with values: `'loading' | 'empty' | 'low-data' | 'ready'`

Use real history point count before artificial fallback points are injected.

- [ ] **Step 2: Run type-check mentally against current component API**

Confirm the new computed values only depend on existing refs/computed state and do not require store API changes yet.

Expected: no unresolved symbols in the page script section.

- [ ] **Step 3: Update chart area template to render by state**

Modify the chart area in `src/pages/history/index.vue` so that:
- `ready` renders the normal chart
- `low-data` renders the chart plus explanatory helper text/current value emphasis
- `empty` renders a clear empty-state block
- `loading` renders a lightweight loading placeholder

Do not remove the existing chart; layer state UI around it.

- [ ] **Step 4: Add low-data helper content**

Expose:
- latest metric value
- latest timestamp
- helper copy explaining the 1h range has limited samples

Expected: 1h can never look like a blank broken card.

- [ ] **Step 5: Run TypeScript verification**

Run: `npm run type-check`
Expected: pass or only pre-existing unrelated issues.

---

### Task 2: Improve chart rendering contrast and interaction correctness

**Files:**
- Modify: `src/components/LineChart.vue`

- [ ] **Step 1: Extend component props for view state**

Add small, explicit props as needed, such as:
- `state?: 'loading' | 'empty' | 'low-data' | 'ready'`
- `helperText?: string`

Keep props optional so existing usage remains compatible if the page is not yet updated.

- [ ] **Step 2: Fix clickable point index mapping**

Unify the sampling step used by:
- `clickableDots`
- `onDotTap()`

Expected: clicking a dot always maps to the correct original data point and popup data.

- [ ] **Step 3: Improve canvas contrast**

Adjust drawing values to improve readability:
- background opacity/tone
- grid line visibility
- x-axis text visibility
- line stroke prominence
- threshold line readability

Expected: chart content remains visible on the existing glassmorphism background.

- [ ] **Step 4: Reduce unnecessary overlay density**

Ensure clickable hotspots do not overpopulate when data volume is large.

Expected: fewer overlay nodes, lower redraw/interaction cost.

- [ ] **Step 5: Make empty/low-data visuals explicit**

Render clearer empty or helper messaging in component/container styling so low-data states do not visually resemble a white blank surface.

- [ ] **Step 6: Run TypeScript verification**

Run: `npm run type-check`
Expected: pass or only pre-existing unrelated issues.

---

### Task 3: Improve history readiness and perceived loading

**Files:**
- Modify: `src/store/device.ts`
- Reference: `src/store/device.ts:160-175`
- Reference: `src/store/device.ts:218-334`

- [ ] **Step 1: Add explicit history sync status fields**

Add minimal store state to describe cloud history readiness, for example:
- `historySyncing`
- `historySyncReady`
- optional `historySyncError`

Do not redesign the store.

- [ ] **Step 2: Wrap cloud sync lifecycle updates**

Update `fetchCloudHistory()` so it sets sync status before/after requests and records failure safely.

Expected: page can distinguish “no data yet” from “still syncing”.

- [ ] **Step 3: Preserve local-first rendering semantics**

Ensure `loadHistory()` data is immediately usable even if cloud sync is still running.

Expected: page does not wait on cloud history before rendering a usable initial state.

- [ ] **Step 4: Consume sync status from history page**

Update `src/pages/history/index.vue` to use the new store sync flags when deciding `chartViewState`.

Expected: loading placeholder appears only when appropriate; local data still wins.

- [ ] **Step 5: Run TypeScript verification**

Run: `npm run type-check`
Expected: pass or only pre-existing unrelated issues.

---

### Task 4: Polish page-level visuals for cohesion

**Files:**
- Modify: `src/pages/history/index.vue`

- [ ] **Step 1: Refine chart card styling**

Tighten the chart card background, border, and shadow so the chart area has stronger depth and less washed-out appearance.

- [ ] **Step 2: Unify tabs and summary styling**

Make range tabs, metric tabs, and stat items feel like the same design system:
- coherent corner radius
- balanced contrast
- consistent active shadows
- cleaner spacing

- [ ] **Step 3: Add dedicated helper/empty/loading styles**

Create specific styles for low-data helper text, empty state, and loading state. Avoid using near-white text over translucent light backgrounds.

- [ ] **Step 4: Review alert log visual consistency**

Make only minor adjustments needed so the chart card and alert log card feel visually aligned.

- [ ] **Step 5: Run TypeScript verification**

Run: `npm run type-check`
Expected: pass or only pre-existing unrelated issues.

---

### Task 5: Final verification

**Files:**
- Verify modified files:
  - `src/pages/history/index.vue`
  - `src/components/LineChart.vue`
  - `src/store/device.ts`

- [ ] **Step 1: Run full type-check**

Run: `npm run type-check`
Expected: success.

- [ ] **Step 2: Run diagnostics on changed files**

Use diagnostics tooling on:
- `src/pages/history/index.vue`
- `src/components/LineChart.vue`
- `src/store/device.ts`

Expected: no new errors.

- [ ] **Step 3: Manually verify acceptance criteria**

Check:
- 1h state is readable and not blank-looking
- low-data/empty/ready/loading are visually distinct
- metric switching still works
- point tap details still match the selected point
- page feels faster because local data shows immediately

- [ ] **Step 4: Summarize any pre-existing issues**

If verification reveals unrelated pre-existing issues, document them separately instead of broadening the fix.
