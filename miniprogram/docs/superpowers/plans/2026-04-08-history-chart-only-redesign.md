# History Chart Only Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild only the history curve chart path so 1h/6h always render, 24h/7d open in a usable viewport immediately, and the chart feels closer to a commercial IoT/data-monitoring app.

**Architecture:** Keep the redesign scoped to the chart chain. Rework `src/components/LineChart.vue` as the main delivery, allow minimal chart-only integration changes in `src/pages/history/index.vue`, and keep all non-chart history-page business UI unchanged. Use a dual-mode chart strategy: fixed viewport for 1h/6h and controlled horizontal viewport for 24h/7d.

**Tech Stack:** Vue 3 `<script setup>`, TypeScript, uni-app canvas, uni-app scroll-view

---

## File Map

### Modify
- `src/components/LineChart.vue`
  - Main chart redesign target
  - Rebuild layout strategy, viewport behavior, point mapping, rendering layers, and tooltip behavior
- `src/pages/history/index.vue`
  - Only chart-related integration code
  - Pass range/mode/config to chart, adjust chart container behavior if needed

### Do Not Modify
- Alert log list behavior in `src/pages/history/index.vue`
- Popup business behavior in `src/pages/history/index.vue`
- `src/store/device.ts` unless absolutely required for chart-only data shaping (avoid if possible)
- Other pages

### Reference
- `docs/superpowers/specs/2026-04-08-history-chart-only-redesign.md`
- Existing chart use in `src/pages/history/index.vue`
- Existing chart implementation in `src/components/LineChart.vue`

---

### Task 1: Redefine chart integration contract

**Files:**
- Modify: `src/pages/history/index.vue`
- Modify: `src/components/LineChart.vue`

- [ ] **Step 1: Add explicit chart mode contract**

Define a simple chart integration contract based on range:
- `compact` mode for `1h` and `6h`
- `expanded` mode for `24h` and `7d`

Pass this explicitly from `src/pages/history/index.vue` into `src/components/LineChart.vue`.

- [ ] **Step 2: Keep non-chart page logic untouched**

Limit page edits to:
- chart props
- chart container sizing/positioning
- chart-only computed values if strictly needed

Do not alter alert list behavior, popup behavior, or unrelated page copy.

- [ ] **Step 3: Run a quick static sanity pass**

Confirm the page still has one chart entry point and no duplicate chart states or incompatible props remain.

Expected: the page remains the same feature-wise except for chart integration.

---

### Task 2: Rebuild 1h/6h chart behavior for fixed viewport

**Files:**
- Modify: `src/components/LineChart.vue`

- [ ] **Step 1: Remove horizontal-scroll dependency for short ranges**

Implement a fixed-width layout path for `compact` mode so `1h` and `6h` always render inside the visible viewport.

Expected: user does not need to scroll to discover the curve.

- [ ] **Step 2: Define stable spacing for sparse data**

Ensure low point counts still generate:
- visible line
- sensible point spacing
- readable axis labels
- no “looks blank” state when values exist

- [ ] **Step 3: Simplify short-range viewport math**

Use container width directly for short ranges. Avoid oversized internal canvas widths for `1h` and `6h`.

Expected: chart appears immediately and predictably.

- [ ] **Step 4: Verify tooltip/point selection still works in compact mode**

Keep point hit testing accurate after layout changes.

Expected: tap target and tooltip value/time match the selected point.

---

### Task 3: Rebuild 24h/7d initial viewport behavior

**Files:**
- Modify: `src/components/LineChart.vue`
- Modify: `src/pages/history/index.vue` (only if required for initial positioning or container behavior)

- [ ] **Step 1: Redesign expanded-mode canvas width strategy**

For `24h` and `7d`, compute chart width based on point density that preserves readability without producing a hostile first viewport.

- [ ] **Step 2: Set correct initial visible region**

Implement a deterministic initial viewport behavior so the chart opens in a usable state immediately.

Expected: no “must aggressively swipe left first” behavior.

- [ ] **Step 3: Keep horizontal exploration available**

Users should still be able to scroll through longer data ranges after first paint.

Expected: first view is good, extended browsing still works.

- [ ] **Step 4: Confirm expanded-mode label density is controlled**

Prevent label collisions and overcrowded tick marks.

Expected: long-range chart stays readable.

---

### Task 4: Rebuild chart rendering layers for commercial-grade clarity

**Files:**
- Modify: `src/components/LineChart.vue`

- [ ] **Step 1: Reorganize rendering order**

Render in a deliberate layer order:
- background
- grid
- threshold lines
- area fill
- main line
- points/abnormal markers
- selection indicator
- tooltip/highlight

- [ ] **Step 2: Improve line and fill styling**

Make the primary line more legible and the area fill more restrained.

Expected: chart reads as polished and professional, not washed out.

- [ ] **Step 3: Improve threshold and abnormal point styling**

Thresholds should be visible but secondary. Alert points should be noticeable without overwhelming the trend.

- [ ] **Step 4: Improve tooltip and selected-point treatment**

Use a clearer selected state and a more product-like tooltip appearance.

Expected: interaction feels intentional, not debug-like.

---

### Task 5: Rebuild point mapping and interaction correctness

**Files:**
- Modify: `src/components/LineChart.vue`

- [ ] **Step 1: Separate render-point sampling from hit-point mapping**

If sampling is used for performance, preserve a stable mapping from displayed/hit-tested points back to source data indices.

- [ ] **Step 2: Ensure nearest-point selection behavior is deterministic**

Selection should consistently resolve to the same logical data point for the same touch location.

- [ ] **Step 3: Validate tooltip payload correctness**

Tooltip must show the exact value/time for the selected source point.

Expected: no mismatch between touched point and displayed data.

---

### Task 6: Keep scope limited to chart-only redesign

**Files:**
- Verify: `src/pages/history/index.vue`
- Verify: `src/components/LineChart.vue`

- [ ] **Step 1: Audit page edits for scope discipline**

Re-read page changes and ensure only chart wiring/container code changed.

- [ ] **Step 2: Remove accidental non-chart changes if introduced**

If any unrelated page business behavior changed during the redesign, revert it.

Expected: redesign stays within the chart-only scope approved by the user.

---

### Task 7: Verification

**Files:**
- Verify changed files:
  - `src/components/LineChart.vue`
  - `src/pages/history/index.vue`

- [ ] **Step 1: Run build verification**

Run: `npm run build:h5`
Expected: `DONE  Build complete.`

- [ ] **Step 2: Run diagnostics on changed Vue files**

Use diagnostics tooling on:
- `src/components/LineChart.vue`
- `src/pages/history/index.vue`

Expected: no new diagnostics.

- [ ] **Step 3: Run type-check if toolchain permits**

Run: `npm run type-check`
Expected: pass, or document pre-existing `vue-tsc` toolchain failure if unchanged from current environment.

- [ ] **Step 4: Manually verify acceptance criteria**

Check:
- `1h` opens with visible curve
- `6h` opens with visible curve
- `24h` does not require aggressive left swipe to become useful
- `7d` does not require aggressive left swipe to become useful
- tapping points shows correct time/value
- alert points and thresholds remain understandable
- chart feels visibly more polished than before

- [ ] **Step 5: Document residual limitations explicitly**

If any remaining issue is outside chart-only scope, note it instead of broadening the change.
