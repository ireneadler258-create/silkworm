# Shared UART1 Scheduler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Centralize UART1 ownership so GPS has priority while voice and CO2 are delayed rather than preempting the UART.

**Architecture:** Introduce a single `UARTManager` as the only creator of `UART(1)`. Refactor GPS, CO2, and voice modules to consume manager-owned UART windows, with GPS reservation windows, queued voice commands, and deferred CO2 polling coordinated from `main.py`.

**Tech Stack:** MicroPython, ESP32-S3, `machine.UART`, existing sensor modules.

---

### Task 1: Define verification approach

**Files:**
- Modify: `docs/superpowers/plans/2026-04-08-uart1-shared-scheduler.md`

- [ ] Step 1: Record a lightweight verification strategy because this project has no automated test harness.
- [ ] Step 2: Verify syntax/diagnostics on all changed Python files.
- [ ] Step 3: Verify that `UART(1` only remains in `uart_manager.py` after refactor.
- [ ] Step 4: Verify `gps_reader.py` accepts both `GP` and `GN` talkers.

### Task 2: Add UART manager

**Files:**
- Create: `uart_manager.py`

- [ ] Step 1: Implement a single-owner `UARTManager` that can acquire, release, and reconfigure UART1.
- [ ] Step 2: Add GPS reservation tracking, voice queue helpers, and CO2 pending helpers.
- [ ] Step 3: Add concise ownership logs for debugging runtime arbitration.

### Task 3: Refactor GPS and CO2 readers

**Files:**
- Modify: `gps_reader.py`
- Modify: `co2_reader.py`

- [ ] Step 1: Replace direct `UART(1, ...)` creation with injected-UART helpers.
- [ ] Step 2: Keep cache semantics intact.
- [ ] Step 3: Extend GPS parsing to support `GPGGA/GPRMC/GNGGA/GNRMC`.

### Task 4: Refactor voice alert and main loop

**Files:**
- Modify: `voice_alert.py`
- Modify: `main.py`

- [ ] Step 1: Convert voice sending to queueing plus manager-driven sending.
- [ ] Step 2: Initialize `UARTManager` in `main.py`.
- [ ] Step 3: Reorder slow-sensor / voice processing so GPS windows run before voice/CO2 work.

### Task 5: Verify refactor

**Files:**
- Modify: `uart_manager.py`
- Modify: `gps_reader.py`
- Modify: `co2_reader.py`
- Modify: `voice_alert.py`
- Modify: `main.py`

- [ ] Step 1: Run diagnostics for changed files.
- [ ] Step 2: Run a repository search for `UART(1` to confirm single-point ownership.
- [ ] Step 3: Report any limitations due to lack of hardware/runtime verification in this environment.
