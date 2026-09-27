# Phase 3 (v2) Implementation Plan

## Overview

Phase 3 expands with data explorer, active learning, pretraining finishing, multi-tenancy tiers, advanced generation, orchestration review, and compliance pack.

## Tasks

### X1 Data Explorer (Lilac-style) — 5 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| X1.1 | Embedding clusters with LLM titles | Cluster 4M docs < 1 h on batch node | 2 ew |
| X1.2 | Semantic + keyword search | Filter < 1 s on 10M rows | 1 ew |
| X1.3 | Facets over accepted/rejected | 0.5 ew |
| X1.4 | Bulk re-queue/reject/tag operations | 1.5 ew |

### X2 Active Learning & Label Quality — 4 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| X2.1 | Uncertainty/disagreement prioritization | 2 ew |
| X2.2 | Confident-learning label-issue scores | 1 ew |
| X2.3 | Retrain quality classifiers from human labels | ≥20% fewer annotations to reach target agreement | 1 ew |

### X3 Pretraining Finishing — 4 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| X3.1 | n-gram decontamination vs registered eval sets | 1.5 ew |
| X3.2 | Mixing recipes with token budgets | 1 ew |
| X3.3 | Megatron `.bin/.idx` export | 1 ew |
| X3.4 | Per-mixture tokenizer stats | Contaminated version blocked from export | 0.5 ew |

### X4 Multi-tenancy Tiers — 4 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| X4.1 | Dedicated namespace/DB tenants | 1 ew |
| X4.2 | Per-tenant redaction keys | 1 ew |
| X4.3 | Quotas and chargeback (tokens, GPU-hours, storage) | Chargeback report per tenant per month | 2 ew |

### X5 Advanced Generation — 4 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| X5.1 | Verifier-based rejection sampling (sandboxed code, math checkers) | 2 ew |
| X5.2 | Agentic trajectory synthesis | 1 ew |
| X5.3 | Offline vLLM on Ray for > 1M rows | 1M-row offline job completes with cost accounting | 1 ew |

### X6 Orchestration Review — 1 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| X6.1 | Evaluate Temporal for cross-system sagas | ADR updated | 1 ew |

### X7 Compliance Pack — 3 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| X7.1 | Audit export to SIEM | 1 ew |
| X7.2 | Retention policies | 0.5 ew |
| X7.3 | Per-export lineage report (sources, licenses, models, annotators) | 0.5 ew |
| X7.4 | External pen test | Pen-test criticals closed | 1 ew |

## Total Effort

- **Phase 3 (v2):** 25 ew + hardening buffer

## Files to Create

```
src/api/
├── core/
│   ├── explorer/
│   │   ├── clustering.py
│   │   ├── search.py
│   │   └── facets.py
│   ├── active_learning/
│   │   ├── uncertainty.py
│   │   ├── confident_learning.py
│   │   └── classifier_retrain.py
│   ├── pretraining/
│   │   ├── decontamination.py
│   │   ├── mixing.py
│   │   └── megatron_export.py
│   ├── multitenancy/
│   │   ├── dedicated_tenants.py
│   │   ├── redaction_keys.py
│   │   └── chargeback.py
│   ├── advanced_generation/
│   │   ├── verifier_sampling.py
│   │   ├── agentic_synthesis.py
│   │   └── offline_vllm.py
│   └── compliance/
│       ├── audit_export.py
│       ├── retention.py
│       └── lineage.py
└── api/v1/endpoints/
    ├── explorer.py
    ├── active_learning.py
    ├── pretraining.py
    ├── multitenancy.py
    ├── advanced_generation.py
    ├── compliance.py
```

## Next Steps

1. Implement X1: Data explorer (Lilac-style)
2. Implement X2: Active learning & label quality
3. Implement X3: Pretraining finishing
4. Implement X4: Multi-tenancy tiers
5. Implement X5: Advanced generation
6. Implement X6: Orchestration review
7. Implement X7: Compliance pack
