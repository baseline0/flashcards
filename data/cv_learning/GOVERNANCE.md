# Hub-and-Spoke Governance — Interview Guide (Quick Reference)

## The Core Problem & Solution

**Problem:** 
- Centralized (hub approves everything) → Slow, bottleneck
- Decentralized (each team makes own rules) → Chaos, compliance nightmare

**Solution (Hub-and-Spoke):**
```
HUB                          SPOKES (Autonomous Teams)
├─ Define policies           ├─ P&C Commercial (underwriting)
├─ Enforce guardrails        ├─ Life Insurance (claims)
├─ Provide paved paths       ├─ Reinsurance (risk transfer)
└─ Audit compliance          └─ [inherit hub standards, deploy autonomously]
```

## How It Works

1. **Hub registers policy:** "All ML models must pass disparate impact audit (DI >= 0.8)"
2. **Spoke builds model:** claims_risk_v2_0 (P&C team)
3. **Registry runs check:** Automated compliance check against hub policies
4. **Result:** 
   - ✅ PASS (DI=0.92) → Deploy immediately (no bottleneck)
   - ❌ FAIL (DI=0.70) → Spoke requests exception with justification
5. **Hub review:** Approve exception (e.g., "synthetic data test") or deny
6. **Audit trail:** Everything logged (model, policy, check date, pass/fail, who approved)

## Key Vocabulary (Interview-Ready)

| Term | Definition | Example |
|------|-----------|---------|
| **Policy** | Hub-defined rule | "All models must pass bias audit" |
| **Guardrail** | Measurable constraint | "DI ratio >= 0.8" |
| **Spoke** | Autonomous domain team | P&C Commercial, Life Insurance |
| **Compliance** | Did artifact follow policies? | Model: PASS (all policies met) |
| **Exception** | Rare policy deviation | "Use synthetic data for testing" |
| **Paved Path** | Pre-built template | ML pipeline template, CI/CD config |
| **Audit Trail** | Complete log | Model v2.0 checked by policy_bias on 2026-09-14 → PASS |

## Interview Talking Points

### "How do you scale governance across multiple teams without bottlenecks?"

> "We use hub-and-spoke governance. The hub team (data platform, ML platform) defines non-negotiable policies—all models must pass fairness audit, all data must be from Gold tables (PII-masked). But we don't have humans approving every model. We built a compliance registry that automatically checks policies. If a model passes all checks, it deploys immediately. If it violates a policy, the spoke team can request an exception with justification. This gives us consistency (everyone follows hub policies), autonomy (spokes don't wait for approval), and auditability (everything logged). At scale: 1 hub team, 10 spoke teams, no bottleneck."

### "What happens when a spoke wants to deviate from hub policy?"

> "They request an exception. For example, Life Insurance team wants to train on synthetic data (before production rollout). That violates our 'data must be from Gold tables' policy. They submit a request with reason and timeline. Hub reviews it, either approves ('okay for testing') or denies ('production requires real data'). The exception is logged with decision, so our audit trail shows: model X used synthetic data under exception EXC-2026-0042, approved by hub on 2026-09-14. Compliance verified."

### "How do you prevent chaos across domains?"

> "Policies are versioned and machine-enforceable. Every spoke inherits the same policy definitions. We track compliance metrics by spoke: P&C Commercial deployed 23 models last month, all passed bias audit; Life Insurance deployed 8 models, 1 had an approved exception. If a spoke repeatedly violates policies, we see it in dashboards and can investigate. And paved paths matter—we provide pre-built model templates that already satisfy hub policies. Spoke teams use those instead of building from scratch."

## Quick Stats

- **Policies:** 4 hub-enforced (bias audit, data lineage, metric conformance, explainability)
- **Spokes:** 3+ (P&C Commercial, P&C Personal, Life Insurance)
- **Workloads:** Each spoke can deploy models/pipelines independently (compliance-checked)
- **Exceptions:** Rare (tracked, approved, audited)
- **Scale:** 1 hub, N spokes, zero bottleneck

---

## Next: Phase 5 (P&C Insurance Domain Depth)

P&C-specific workflows: underwriting, claims triage, reserve estimation, fraud detection.
