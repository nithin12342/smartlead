# D12 — smartlead · Detailed Completion Plan

*Source evidence: reports/smartlead.md (execution-verified 2026-08-24) · nodes D12-1..D12-DEPLOY
from deployment_ready_minimum_diff_plan.md · intent from project_intent_analysis.md §D12.*

---

## 0. Identity

| Field | Value |
|---|---|
| Local path | `C:\Users\thela\Downloads\projects context\SmartLead` |
| Remote | `github.com/nithin12342/smartlead` |
| Branch | `master` (synced 2026-08-25) |
| Intent | Rank sales leads by predicted conversion probability so sellers work the top of the list first — small, honest, production-shaped ML service |
| Input → Output | lead JSON (title, company size, industry, country, source…) → deterministic feature engineering → XGBoost → `{conversion_probability, grade A-D, feature_importances}`; /model/info exposes real holdout AUC |
| Deploy target | Render free scoring API backed by a REAL trained model artifact |
| Verdict at study time | 🟡 Partial — best-engineered of its batch (35/35 tests pass, real API layer), but the ML is fake: no training script/dataset/artifact anywhere, and the fallback **fits XGBoost on `np.random.rand(100,10)`** so out-of-the-box predictions are noise |
| Estimated effort | ~half day |

## 1. Verified defect inventory

| # | Defect | Exact location | Reproduced? |
|---|---|---|---|
| B1 | Random-data model fabrication as production fallback | `src/ml/predictor.py:74-83` (`_create_default_model` fits on random arrays) | ✅ 35 tests pass BECAUSE of this fallback |
| B2 | No training pipeline, no dataset, no *.pkl artifact anywhere in repo | repo tree (glob for pkl/joblib/model = none) | ✅ probes |
| B3 | Success criteria unverifiable: no eval harness/holdout/metric code for "AUC>0.85" or "p99<100ms" | repo tree + README claims | ✅ grep |
| B4 | Fake SHAP: `_get_shap_values()` returns `feature_importances_` labeled SHAP | `src/ml/predictor.py:150-160` | ✅ read |
| B5 | Model path hardcoded to nonexistent file → fallback always triggers | `src/api/config.py:40` (`/models/lead_conversion_model.pkl`) | ✅ probe |
| B6 | Feast/Airflow claims with zero corresponding artifacts; feast==0.35.0 dead-weight pin | requirements.txt, README, COMPLIANCE_REPORT | ✅ grep 0 hits in src/tests |
| B7 | Observability collection hard-fails without opentelemetry-sdk installed | test collection ImportError (env note) | ✅ pytest run |
| B8 | Frontend ModelPerformance.js has no backend endpoint to display | frontend page vs API routes | ✅ inspection |

## 2. Node plan

### P0 RUN-FIX

**Node D12-1 — random-model fallback dies**
```
GOAL      : missing model file = loud startup failure with train instructions;
            never silent noise.
LOCATION  : src/ml/predictor.py:74-83
MIN-DIFF  : _create_default_model → raise ModelNotFoundError with train command hint
VERIFY    : delete/rename any .pkl → start app → exits loudly with message.
            Artifact: verification/d12-1_failfast.txt
SIBLINGS  : re-run existing 35-test suite (some predictor tests may need updating to
            inject a fixture model — allowed within same responsibility)
```

### P1 VERIFY (the real model)

**Node D12-2 — a training pipeline exists**
```
GOAL      : committed script produces a real trained artifact + honest holdout AUC number.
LOCATION  : NEW src/ml/train.py (~120 lines): UCI bank-marketing CSV mapped to the
            existing 10 feature names; chronological/random split 80/20 documented;
            XGBClassifier fit; metrics printed; joblib.dump → models/lead_conversion_model.pkl;
            local MLflow log optional
VERIFY    : python -m ml.train   (dataset fetched by script or committed small sample)
EXPECTED  : artifact created + AUC printed AND RECORDED AS-IS vs 0.85 target (honesty rule).
            Artifact: verification/d12-2_auc.txt + models/ artifact (or download script)
SIBLINGS  : D12-1 fail-fast gate re-run (now passes because artifact exists)
```

**Node D12-3 — eval reproducible**
```
GOAL      : re-running evaluation reproduces the published AUC ±ε.
LOCATION  : NEW scripts/evaluate.py (loads saved artifact, re-runs holdout eval)
VERIFY    : python scripts/evaluate.py → same AUC. Artifact: verification/d12-3_eval.txt
TAG       : ckpt-runs
```

### P2 HARDEN

**Node D12-4 — explanation honest**
```
GOAL      : API field tells the truth about what it returns.
LOCATION  : src/ml/predictor.py:150-160 + response models in src/api/models.py
MIN-DIFF  : rename shap_values → feature_importances (API field versioned); tests updated
VERIFY    : schema diff + pytest green. Artifact: verification/d12-4_schema.txt
```

**Node D12-5 — deps pruned**
```
GOAL      : clean py3.11 install without unused heavy pins.
LOCATION  : requirements.txt (remove torch/feast/mlflow-cloud until used)
VERIFY    : fresh venv pip install -r requirements.txt && pytest -q green.
            Artifact: verification/d12-5_venv.txt
```

**Node D12-6 — perf claim measurable**
```
GOAL      : p99 measured once and published next to AUC, whatever it is.
LOCATION  : NEW locust/hey one-shot script against local uvicorn
VERIFY    : run transcript with p99 number. Artifact: verification/d12-6_perf.txt
SIBLINGS  : all prior gates re-run top-down before tag
TAG       : ckpt-tested   (+ GET /model/info endpoint wired to ModelPerformance.js —
            metadata json shipped beside artifact: version/trained-at/holdout-AUC)
```

### P3 DEPLOY

**Node D12-DEPLOY — public scorer**
```
LOCATION  : Render free web service; model artifact baked into image or release asset
VERIFY    : two distinct leads via public API → distinct probabilities (anti-random proof);
            /health + /docs reachable
PROOF     : transcript + URL → verification/d12_deploy_proof.txt. Tag ckpt-deployed.
ROADMAP    : Feast feature store · Airflow retraining DAGs · real SHAP integration ·
            AKS terraform (replaced by Container Apps consumption if ever needed)
```

## 3. Out of scope (ROADMAP)

Feast registry · Airflow orchestration · torch (unused pin removed) · full AKS+ACR terraform apply
(student-budget trap per report).

## 4. Execution contract

POST-FIX scope check per node · sibling gates re-run before tags · evidence committed atomically ·
tags pushed same day · toolchain: Python ✓ + xgboost/scikit-learn/joblib (pip at batch start).

## 5. P4 — PRODUCTION READINESS DELTA (target: `prod-ready` tag, L4)

Current level after P3 ≈ L3.
| Cat | Gap | Node | VERIFY artifact |
|---|---|---|---|
| G1/G2 | Batch endpoint abuse (1000×large payloads); no request size cap documented | D12-P4a: payload caps enforced + 413/422 paths tested | rejection transcript |
| G2+ | Deps unscanned; Redis-off path untested in CI | D12-P4b: pip-audit green; CI matrix runs with REDIS_URL unset (in-memory fallback proven) | audit log + matrix green |
| G3 | Model artifact lifecycle: version, hash, retrain trigger undefined | D12-P4c: model manifest (hash/trained-at/AUC) shipped beside artifact + drift/retrain policy in RUNBOOK (AUC floor regression test already in suite) | manifest + regression test output |
| G5 | Metrics exist but nothing watches; no error tracking | D12-P4d: uptime monitor on /health; Sentry free tier on exceptions | monitor + Sentry event sample |
| G6/G8 | Rollback = prior model version redeploy; documented + drilled | D12-P4e: rollback drill via MODEL_PATH env switch | drill transcript |
| G7 | p99 measured once locally (D12-6) but not under public load | D12-P4f: post-deploy burst test p99 recorded next to AUC in README | load transcript |

TRACK=product.

### P4 audit addendum (production-readiness pass)
| Cat | Gap found in audit | Node | VERIFY artifact |
|---|---|---|---|
| G4 | Coverage + merge-blocking unstated | D12-P4g: coverage report in required checks (existing 35-test suite + integration from D12 suite); branch protection | coverage + protection screenshot |
| UB | Universal Baseline UB1-UB6 applies (uptime already P4d) | D12-P4h: LICENSE, gitleaks job, pip-audit job, README badge row with AUC + p99 published | per-UB artifacts |

