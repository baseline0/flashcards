# MLOps & Model Registry — Wawanesa Interview Guide

## What is MLOps?

**MLOps** is the engineering framework for managing machine learning systems at scale, from experimentation through production deployment to monitoring and retraining. For insurance, where models drive underwriting risk decisions, MLOps means rigorous auditability: every model prediction must be explainable and provably fair.

**Problem it solves:**
- Without MLOps: A model works in development but fails in production. No audit trail. No way to prove it's not discriminatory.
- With MLOps: Every experiment is logged, every model version is tested for fairness, all predictions are explained, audit trail is complete.

---

## Model Approval Workflow (ASCII Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                   MODEL APPROVAL WORKFLOW                        │
└─────────────────────────────────────────────────────────────────┘

                          DATA SCIENTIST
                                │
                                ▼
        ┌──────────────────────────────────────┐
        │  EXPERIMENT                          │
        │  ─────────────────────────────────   │
        │  • Algorithm: XGBoost                 │
        │  • Data: gold.claims_2024_q1          │
        │  • Hyperparams: max_depth=7, lr=0.05 │
        │  • Metrics: AUC=0.89, F1=0.87        │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  MODEL REGISTRATION                  │
        │  ─────────────────────────────────   │
        │  claims_risk_scoring@1.0              │
        │  Status: STAGING                     │
        │  Approval: PENDING ⏳                 │
        └──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │  FAIRNESS AUDIT                      │
        │  ─────────────────────────────────   │
        │  • Disparate Impact Ratio: 0.92 ✅   │
        │    (>= 0.8: no material bias)        │
        │  • Calibration Error: 0.03 ✅        │
        │    (< 0.05: well-calibrated)         │
        │  • SHAP logging enabled ✅           │
        └──────────────────────────────────────┘
                      │              │
          APPROVED ✅ │              │ REJECTED ❌
                      ▼              ▼
    ┌──────────────────────┐  ┌──────────────┐
    │  Status: APPROVED    │  │  Retrain or  │
    │  Approval: APPROVED  │  │  Investigate │
    │                      │  │  Bias Issues │
    │  Ready for Promotion │  └──────────────┘
    └──────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │  PRODUCTION PROMOTION                │
    │  ─────────────────────────────────   │
    │  Status: STAGING → PRODUCTION        │
    │  Old v0.9: ARCHIVED (rollback ready) │
    │  New v1.0: ACTIVE                    │
    └──────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │  SERVING & MONITORING                │
    │  ─────────────────────────────────   │
    │  • Batch Scoring: 1M claims/night    │
    │  • Real-time API: claims as arrive   │
    │  • SHAP Logging: every prediction    │
    │  • Drift Detection: accuracy SLA     │
    │  • Audit Trail: complete lineage     │
    └──────────────────────────────────────┘
```

---

## Model Lifecycle (The 5 Stages)

### 1. **Experiment** — Training Run
You train a model with specific:
- Algorithm (e.g., XGBoost)
- Data (e.g., `gold.claims_2024_q1`)
- Hyperparameters (max_depth=7, learning_rate=0.05)
- Train/val/test splits (70% / 15% / 15%)

Result: Metrics (AUC-ROC=0.89, F1=0.87)

### 2. **Model Registration** — Versioning
Promote the experiment to a versioned artifact:
- Model name: `claims_risk_scoring`
- Version: `1.0` (semver: MAJOR.MINOR)
- Status: `STAGING` (candidate, not yet approved)
- Approval: `PENDING` (awaiting fairness audit)

### 3. **Bias Audit** — Fairness Validation
Before production, check for discrimination:
- **Disparate Impact Ratio (DI)**: Does the model treat women and men equally?
  - DI = (approval rate for women) / (approval rate for men)
  - DI >= 0.8: Generally acceptable
  - DI < 0.8: Regulatory risk (potential discrimination)
- **Calibration**: Do predicted probabilities match actual outcomes?
  - For 1000 predictions of ~0.7, did ~700 actually occur?
- **Result**: APPROVED or REJECTED

### 4. **Production Promotion**
If bias audit passes:
- Status: `STAGING` → `PRODUCTION`
- Old production model: archived (can roll back if needed)
- All previous models: versioned history (never deleted)

### 5. **Serving & Monitoring**
- Batch scoring: Score 1M claims in a nightly job
- Real-time serving: Score claims as they arrive (API)
- Monitoring: Track prediction drift (is model still accurate?)
- Retraining trigger: If accuracy drops below SLA

---

## Key Vocabulary

### Model Management

| Term | Definition | Example |
|------|-----------|---------|
| **Experiment** | Single training run (data, code, hyperparams, metrics) | `exp_20260914_xgb_001` |
| **Model Version** | Trained artifact with approval status | `claims_risk_scoring@1.0` (staging, pending audit) |
| **Experiment Tracking** | Log all training runs for reproducibility | Side-by-side comparison of 10 different hyperparam choices |
| **Model Registry** | Version-controlled repository of trained models | Query: "Get all production models", "List versions of claims_risk_scoring" |
| **Approval Workflow** | Staging → Validation → Production | New model must pass bias audit before promotion |

### Fairness & Explainability

| Term | Definition | Example |
|---|---|---|
| **Disparate Impact Ratio (DI)** | Bias metric (protected rate ÷ reference rate) | DI=0.75 (women 25% less likely to be approved) |
| **Disparate Impact** | When DI < 0.8 (potential discrimination) | "This model exhibits disparate impact against women" |
| **Calibration** | Do predicted probabilities match actual outcomes? | "For 1000 predictions of 0.7, 720 actually occurred" ✅ |
| **SHAP Values** | Per-prediction feature importance | Prediction=0.73 (high-risk) because: claim_amount (+0.22), days_since_policy (+0.15), injury_type (+0.18) |
| **Explainability** | Ability to justify why model made a prediction | Auditor asks: "Why did you deny this claim?" → See SHAP values |

### Business Context

| Term | Definition | Why It Matters |
|---|---|---|
| **Model Drift** | Prediction distribution changed | Model may need retraining if output distribution shifts |
| **Data Drift** | Input distribution changed | Model may not work on new data (e.g., economic downturn changes claim patterns) |
| **Fairness Compliance** | Models must not discriminate (FCRA, FHA, Fair Lending) | Regulatory requirement in financial services |
| **Audit Trail** | Complete history of model creation, approval, deployment | "When this decision was made, this model version was in production, and here's its fairness audit" |

---

## Our Implementation

### Module Structure

```
src/agent_system/workflow/mlops/
├── __init__.py           # Module docstring with full vocabulary
├── models.py             # Experiment, Model, ModelMetrics, BiasAuditResult, SHAPExplanation
├── registry.py           # ModelRegistry (versioning, approval workflow, SHAP logging)
└── bias_detection.py     # DisparateImpactAnalysis, CalibrationMetrics, BiasAudit

tests/unit/
└── test_mlops.py         # 25 tests covering registry, bias, explainability
```

### Key Classes

**Experiment** (in `models.py`):
```python
exp = Experiment(
    model_name="claims_risk_scoring",
    experiment_id="exp_20260914_xgb_001",
    algorithm="xgboost",
    training_data_table="gold.claims_2024_q1",
    hyperparams={"max_depth": 7, "learning_rate": 0.05},
    metrics=ModelMetrics(auc_roc=0.89, f1_score=0.87),
)
```

**Model** (versioned artifact):
```python
model = Model(
    name="claims_risk_scoring",
    version="1.0",
    experiment_id="exp_20260914_xgb_001",
    status=ModelStatus.STAGING,
    approval_status=ApprovalStatus.PENDING,  # Awaiting bias audit
    metrics=ModelMetrics(...),
)
```

**BiasAuditResult** (fairness audit):
```python
audit = BiasAuditResult(
    model_name="claims_risk_scoring",
    model_version="1.0",
    disparate_impact_ratio=0.92,  # >= 0.8: acceptable
    calibration_error=0.03,       # < 0.05: well-calibrated
    passed_audit=True,            # ✅ Ready for production
)
```

**SHAPExplanation** (per-prediction explainability):
```python
explanation = SHAPExplanation(
    prediction_id="pred_20260914_claim_12345",
    prediction_value=0.73,  # 73% probability of high-risk
    shap_values={
        "days_since_policy": 0.15,   # Positive → increases risk
        "claim_amount": 0.22,        # Positive → increases risk
        "injury_type_fracture": 0.18,
    },
)
# Output: "High-risk (73%) because: claim_amount (+0.22), days_since_policy (+0.15)"
```

**ModelRegistry** (in `registry.py`):
```python
registry = ModelRegistry.load_default()

# 1. Register an experiment
registry.register_experiment(exp)

# 2. Create model from experiment
model = registry.create_model_from_experiment(exp, version="1.0")

# 3. Run bias audit
audit = BiasAudit.run(model_name="claims_risk_scoring", ...)
registry.record_bias_audit("claims_risk_scoring", "1.0", audit)

# 4. Promote to production (if audit passes)
registry.promote_to_production("claims_risk_scoring", "1.0")

# 5. Log SHAP explanations for audit trail
registry.log_prediction_explanation(explanation)

# Query operations
prod_model = registry.get("claims_risk_scoring", "1.0")  # Retrieve model
exps = registry.list_experiments("claims_risk_scoring")  # All training runs
audit = registry.get_bias_report("claims_risk_scoring", "1.0")
explanations = registry.get_explanations("claims_risk_scoring", limit=100)
```

---

## Interview Talking Points

### When They Ask: "How do you ensure models are fair and compliant in production?"

**Your Answer (using MLOps vocabulary):**

> "Every model goes through a standardized approval workflow. Before production, we run a fairness audit that checks for disparate impact—essentially, does the model treat protected groups (women, minorities, younger people) differently than reference groups? We measure the disparate impact ratio: if it's below 0.8, it flags regulatory risk and the model is rejected. We also check calibration—do predicted probabilities match actual outcomes? Once approved, every model is versioned in a registry, so we have a complete audit trail: who trained it, when, on what data, and what was the fairness audit result. Then, crucially, every prediction in production is logged with SHAP values, so auditors can answer 'Why did the model deny this claim?' with specific feature importance scores."

### When They Ask: "What happens if a model starts failing in production?"

**Your Answer:**

> "We have full version history. If model v2.0 underperforms, we can instantly roll back to v1.0, which is still in our registry. Monitoring tracks prediction drift continuously. If accuracy drops below SLA, we trigger retraining on recent data. Because we log all predictions with SHAP values, we can also analyze: is the model failing on a specific claim type? Is data distribution different? That guides whether we retrain or need a new approach entirely."

### When They Ask: "How do you handle the difference between model accuracy and business impact?"

**Your Answer:**

> "MLOps separates these concerns. We track both. A model might have excellent AUC-ROC (statistical accuracy) but poor calibration (predicted probabilities don't match reality). We might have a well-calibrated model (probabilities accurate) but it exhibits disparate impact. We report both the technical metrics (AUC, F1, calibration error) and the fairness metrics (disparate impact ratio per demographic group) to the business. Business can then decide: 'We want to retrain because this model unfairly disadvantages women,' not as a guess, but backed by fairness audit data."

---

## Real-World Scenario: P&C Claims Risk Model

1. **Data Science** trains a claims risk model on `gold.claims_2024_q1`
   - Algorithm: XGBoost
   - Features: days_since_policy, claim_amount, injury_type, police_report_filed
   - Metrics: AUC=0.89, F1=0.87

2. **Model is registered** as `claims_risk_scoring@1.0` in STAGING

3. **Fairness audit** is run:
   - Disparate Impact Analysis:
     - Female approval rate: 72%
     - Male approval rate: 75%
     - DI = 0.72 / 0.75 = 0.96 ✅ (acceptable, >= 0.8)
   - Calibration: error=0.03 ✅ (good)
   - Result: APPROVED

4. **Model is promoted** to PRODUCTION (v1.0)

5. **A new claim arrives:** $8000 for a fractured arm, filed 12 days after policy purchase
   - Model predicts: 0.73 (73% probability of high-risk)
   - SHAP explanation logged:
     - claim_amount=$8000: +0.22 (increases risk)
     - days_since_policy=12: +0.15 (increases risk)
     - injury_type=fracture: +0.18 (increases risk)
   - Policy: "Deny claims >0.70 threshold"
   - Decision: DENY

6. **Auditor asks:** "Why was this claim denied?"
   - Response: "Based on fairness-audited model v1.0, the claim exceeded our risk threshold. Here's the explanation: recent policy, high claim amount, and injury type all indicated elevated risk. We logged that the model exhibited no material bias against any demographic group in pre-production testing."

---

## Next Steps (Phases 3-5)

1. ✅ **Semantic Layer** — Canonical metric definitions
2. ✅ **MLOps & Model Registry** — DONE (today)
3. 📝 **Operational Intelligence** — Log analysis, AI-assisted incident diagnosis
4. 📝 **Hub-and-Spoke Governance** — Operational demonstration of policy enforcement
5. 📝 **P&C Domain Depth** — Underwriting workflows, NAIC standards, risk models

---

## Quick Reference: Fairness Thresholds

| Metric | Threshold | Interpretation |
|--------|-----------|-----------------|
| Disparate Impact Ratio | >= 0.8 | No material bias detected |
| Disparate Impact Ratio | 0.75-0.79 | Borderline; manual review |
| Disparate Impact Ratio | < 0.75 | Significant bias risk; reject model |
| Calibration Error | < 0.05 | Well-calibrated; probabilities trustworthy |
| Calibration Error | > 0.10 | Poorly calibrated; predictions unreliable |
| AUC-ROC | > 0.80 | Acceptable discrimination ability |
| F1 Score | > 0.80 | Good precision/recall balance |
