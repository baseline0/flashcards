# Operational Intelligence — Wawanesa Interview Guide

## What is Operational Intelligence?

**OI** is the bridge between observability (logs, metrics, traces) and action. When a service fails, you have thousands of log lines. OI's job:

```
Logs → Aggregate → Detect Anomaly → Diagnose (LLM) → Remediate → Track SLA
```

**Problem it solves:**
- Without OI: An engineer stares at logs for 30 minutes to figure out "database connection pool exhausted"
- With OI: Logs aggregated → anomaly detected automatically → LLM diagnosis in seconds → auto-scale applied in 1 minute

---

## The Incident Lifecycle (5 Stages)

### 1. **Detection** — Alert Fires
Alert rule triggers: "Error rate > 5% for 5+ minutes"
→ Incident created with severity and summary

### 2. **Acknowledgment** — On-Call Responds
On-call engineer sees alert, acknowledges (MTTA tracked)

### 3. **Investigation** — Root Cause Analysis
LLM analyzes aggregated logs:
- Patterns: "Connection pool, timeout, exhausted" → RCA: database saturation
- Confidence: High (multiple matching patterns)
- Remediation suggestions: auto (scale) + manual (config change)

### 4. **Remediation** — Fix Applied
Auto-remediations execute immediately (scale, restart, clear cache)
Manual remediations queued for approval (config change, deploy patch)

### 5. **Resolution** — Monitor Stability
Incident closed when error rate returns to baseline
MTTR tracked (time from creation to resolution)

---

## Key Vocabulary (SRE Best Practices)

### Incident Classification

| Term | Definition | Example |
|------|-----------|---------|
| **Incident Severity** | SEV1-4 scale (critical → low impact) | SEV2: Claims API degraded, some users affected |
| **SEV1 (Critical)** | Service down, customers blocked | All claims approvals timing out |
| **SEV2 (High)** | Degraded, some users affected | 8% error rate, claim triage delayed |
| **SEV3 (Medium)** | Error rate elevated, limited impact | 2% error rate, no customer-facing impact |
| **SEV4 (Low)** | Cosmetic, no customer impact | Log file rotation failed |

### SLA Metrics

| Term | Definition | Target |
|------|-----------|--------|
| **MTTA** | Mean Time To Acknowledge | < 5 minutes (how fast on-call responds) |
| **MTTR** | Mean Time To Resolution | < 15 minutes (how fast you fix it) |
| **MTBF** | Mean Time Between Failures | > 720 hours (30 days reliability) |
| **Uptime** | Percentage time service is available | 99.9% (9 hours down/month) |

### Remediation

| Term | Definition | Example |
|------|-----------|---------|
| **Auto-Remediation** | Low-risk fix executed immediately | Restart pod, scale up, clear cache |
| **Manual Remediation** | High-risk fix requiring approval | Config change, database migration, deploy |
| **Remediation Playbook** | Template for handling specific incident type | "Database exhaustion: (1) scale, (2) increase pool" |
| **Rollback** | Undo previous fix if it made things worse | Revert to v1.0 if v2.0 makes errors worse |

### Observability & Analysis

| Term | Definition | Example |
|------|-----------|---------|
| **Log Aggregation** | Centralized collection (Splunk, Datadog, ELK) | Query: "Errors in claims-api last hour" |
| **Structured Logs** | JSON format with queryable fields | `{"service":"claims-api", "level":"error", "latency_ms":5000}` |
| **Anomaly Detection** | Alert when metrics exceed baseline | Error rate goes 0.5% → 8% |
| **Root Cause Analysis (RCA)** | Find underlying problem | "Database connection pool exhausted" not "API returned error" |
| **Correlation** | Link related errors across services | Claims API timeouts → Database service latency spike |

### Culture

| Term | Definition | Why It Matters |
|------|-----------|-----------------|
| **Blameless Postmortem** | Focus on "how do we prevent this" not "who broke it" | Engineers don't hide failures; team learns |
| **Alert Fatigue** | Too many alerts → team ignores them | Bad: 100 alerts/day, 99 are false positives |
| **Observability** | Can you understand system from external outputs? | Better: "Why is latency high?" vs. "Is latency high?" |
| **On-Call Friendly** | Only alert when actionable (no noise) | Good: "Connection pool saturated" vs. "Error rate up" |

---

## Our Implementation

### Module Structure

```
src/agent_system/workflow/operational_intelligence/
├── __init__.py           # Module docstring
├── incidents.py          # Incident, LogEvent, AlertRule, IncidentTimeline
├── diagnosis_engine.py   # DiagnosisEngine (logs → RCA → suggestions)
├── remediation.py        # Remediation, RemediationType, RemediationPlaybook
└── registry.py           # IncidentRegistry (lifecycle, SLA, postmortem)

tests/unit/
└── test_operational_intelligence.py  # 25 tests
```

### Example Incident (P&C Claims)

```
TIME: 2026-09-14 10:23 AM

1. DETECTION (10:23)
   Alert: claims-api error_rate > 5%
   Incident created: INC-20260914-0001
   Severity: SEV2
   Summary: "Claims API error rate spike to 8%"

2. ACKNOWLEDGMENT (10:24 - MTTA: 1 minute)
   On-call acknowledges incident
   Status: ACKNOWLEDGED

3. INVESTIGATION (10:24-10:27)
   Aggregated logs show:
   - "Connection pool exhausted" (200 occurrences)
   - "Database timeout" (150 occurrences)
   - Peak QPS: 2000 (vs. 1000 baseline)
   
   DiagnosisEngine analysis:
   Root Cause: "Connection pool saturation due to spike in claim volume"
   Confidence: 85%
   Contributing: "Claim volume 2x normal due to marketing campaign"
   
   Suggested Remediation:
   AUTO: Scale database read replicas (3→5)
   MANUAL: Increase connection pool size (25→50)

4. REMEDIATION (10:27-10:28)
   Auto-remediation executed:
   ✓ Database replicas scaled 3 → 5
   ✓ Load balanced across new replicas
   
   Manual remediation queued:
   ⏳ Connection pool config pending approval

5. RESOLUTION (10:29 - MTTR: 6 minutes)
   Error rate drops to 0.5%
   Incident resolved
   Timeline: Detected (1m) → Ack (1m) → Fixed (4m)

6. POSTMORTEM (10:30)
   Summary: Connection pool too small for peak load
   Root Cause: Campaign planning didn't account for API load
   Action Items:
   - Increase default connection pool to 50
   - Add connection pool saturation alert
   - Update capacity planning for marketing campaigns
   - Blameless focus: "No individual blame; process failed to account for load"
```

---

## Interview Talking Points

### When They Ask: "How do you handle production incidents?"

**Your Answer (using OI vocabulary):**

> "We have a three-layer system. First, structured logging: every service emits JSON logs with correlation IDs and latency metrics. Second, automated detection: alert rules trigger on error rate, latency, or resource saturation. Third, AI-assisted diagnosis: when an alert fires, our system aggregates relevant logs and uses LLM pattern matching to suggest root cause in seconds. For example, if claims-api error rate spikes, the engine correlates it with database connection pool logs and suggests 'Connection pool exhaustion.' We execute auto-remediations (scale, restart) immediately and queue manual changes for approval. Everything is tracked for SLA: MTTA (time to ack), MTTR (time to resolve). And we run blameless postmortems—focus on process, not blame—so the team learns and prevents recurrence."

### When They Ask: "What's your on-call experience like?"

**Your Answer:**

> "Our on-call is designed to be friendly—we alert only on actionable, high-confidence incidents. No alert fatigue. When an incident is declared, the system has already aggregated logs and run diagnosis, so the engineer gets a summary: 'Database connection pool exhausted, try scaling replicas.' Auto-remediations have often already fired by the time they acknowledge. For complex issues, they can dig into the incident timeline and related logs. MTTA target is <5 minutes; MTTR <15 minutes. If SLA is missed, we review in postmortem and add automation or monitoring to prevent recurrence."

### When They Ask: "How do you measure operational excellence?"

**Your Answer:**

> "Three KPIs: MTTA (how fast we notice and ack), MTTR (how fast we fix), and MTBF (how often things break). We track incidents by severity, service, and root cause. This reveals patterns: if database timeouts are 40% of incidents, we know to invest in database reliability. We run blameless postmortems, so incidents aren't hidden—they're learning opportunities. And we measure alert quality: false positive ratio (how many alerts don't need action) is a key metric—high false positive ratio means alert fatigue and slower response to real issues."

---

## Wawanesa Context

For Wawanesa's Senior Application Developer role:

**Claims Processing Pipeline** (real-world example):
- Services: claims-api, underwriting-service, payment-processor
- SLA: <100ms p99 latency, 99.95% uptime (2 hours down/month)
- Incidents logged in ServiceNow, with auto-create from OI system
- On-call rotation: 1 engineer per week, paged via PagerDuty

**Typical SEV2 Incident:**
```
10:15 - Alert: underwriting-service latency p99 > 500ms
10:16 - Incident created, on-call paged
10:17 - Auto-scaling initiated (replicas 3→5)
10:21 - Latency back to 80ms, incident resolved
10:22 - Postmortem scheduled for next day
```

**Red Flags They Watch For:**
- MTTA > 10 minutes (on-call not responsive)
- MTTR > 30 minutes (diagnosis/fix too slow)
- Repeat incidents (same root cause, not fixed)
- False positive alerts > 50% (alert fatigue)

---

## Quick Reference: Incident Severity Decision Tree

```
Is the service down for all users?
├─ YES → SEV1 (page manager, ceo, etc.)
└─ NO:
    Are some users affected (errors, timeouts)?
    ├─ YES → SEV2 (page on-call)
    └─ NO:
        Is error rate or latency elevated but tolerable?
        ├─ YES → SEV3 (ticket, discuss in standup)
        └─ NO:
            Is this only cosmetic/log noise?
            └─ YES → SEV4 (backlog, fix in next sprint)
```

---

## Wawanesa-Specific Vocabulary

| Term | Wawanesa Context |
|------|-----------------|
| **Claims API** | External-facing API for claimants to file claims |
| **Underwriting Service** | Internal service that approves/denies claims |
| **Policy Lookups** | Verify customer policy (active, coverage, etc.) |
| **Premium Calculations** | Compute claim payout (loss ratio, reserves, etc.) |
| **Fraud Detection ML** | ML pipeline flagging suspicious claims |
| **Regulatory Audit Trail** | CCPA, Fair Lending compliance logs |

---

## Next Steps (Phases 4-5)

1. ✅ **Semantic Layer** — Canonical metric definitions
2. ✅ **MLOps & Model Registry** — Model lifecycle + fairness audit
3. ✅ **Operational Intelligence** — DONE (today)
4. 📝 **Hub-and-Spoke Governance** — Operational demonstration of policy enforcement
5. 📝 **P&C Domain Depth** — Underwriting workflows, NAIC standards, risk models
