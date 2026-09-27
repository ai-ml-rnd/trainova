# Phase 1 Implementation Tasks (M2.2-M7.3)

## Status Overview

| Epic | Status | Completion |
|---|---|---|
| M1.1-M1.3 | ✅ Complete | 100% |
| M2.1 | ✅ Complete | 100% |
| M2.2-M2.4 | ⏳ In progress | 0% |
| M3.1-M3.4 | ⏳ Pending | 0% |
| M4.1-M4.2 | ⏳ Pending | 0% |
| M5.1-M5.4 | ⏳ Pending | 0% |
| M6.1-M6.2 | ⏳ Pending | 0% |
| M7.1-M7.3 | ⏳ Pending | 0% |

---

## M2.2 Exact + MinHash Dedup (2 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M2.2.1 SHA-256 exact dedup | Dedup on 1M docs in < 5 min | 0.5 ew |
| M2.2.2 MinHash-LSH (5-gram, 14×8) | Recall ≥ 0.9 on labeled subset | 1 ew |
| M2.2.3 Union-find clustering | Cluster IDs stored in `dup_cluster_id` | 0.5 ew |
| M2.2.4 Resumability | Kill + resume yields identical output hash | 0 ew |

**Tests:**
- On 10M-doc sample, recall ≥ 0.9 vs brute-force Jaccard ≥ 0.8
- Kill worker mid-dedup → resume produces same clusters

---

## M2.3 PII Operator (1 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M2.3.1 Presidio + regex detection | ≥98% of seeded PII detected | 0.5 ew |
| M2.3.2 Redaction modes | tag/redact/hash/replace working | 0.3 ew |
| M2.3.3 Encrypted redaction map | Stored encrypted with tenant key | 0.2 ew |

**Tests:**
- Seed 100 PII instances → verify ≥98% detected
- Cross-tenant redaction maps isolated

---

## M2.4 Token Stats (1 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M2.4.1 Tokenizer-aware counting | Counts match manual calculation | 0.5 ew |
| M2.4.2 Configurable tokenizer | Via schema configuration | 0.3 ew |
| M2.4.3 Length histograms | 100 buckets, 0–512k tokens | 0.2 ew |

**Tests:**
- 100k rows → token counts verified
- Kill + resume → identical hash

---

## M3.1 Pipeline Compiler (2 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M3.1.1 Pipeline spec schema | YAML/JSON spec validated | 1 ew |
| M3.1.2 LangGraph compiler | DAG compiles to StateGraph | 0.5 ew |
| M3.1.3 Postgres checkpointer | State persisted per batch | 0.5 ew |

**Tests:**
- Invalid DAG (cycle, missing column) → validation error
- Valid DAG compiles without errors

---

## M3.2 Task Library (1.5 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M3.2.1 Self-instruct template | Golden snapshot test passes | 0.5 ew |
| M3.2.2 Evol-instruct template | Golden snapshot test passes | 0.5 ew |
| M3.2.3 Multi-response | Model A/B responses generated | 0.5 ew |

**Tests:**
- 20 rows with mock LLM → golden snapshot match

---

## M3.3 LiteLLM Client (1.5 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M3.3.1 Per-run key minting | Virtual key created via LiteLLM API | 0.5 ew |
| M3.3.2 Route semaphores | Constrained by vLLM `max_num_seqs` | 0.5 ew |
| M3.3.3 Response caching | Unchanged rerun → zero LLM calls | 0.5 ew |

**Tests:**
- Rerun identical pipeline → cache hit (zero calls)
- Budget exhaustion → `429 Too Many Requests`

---

## M3.4 Preview and Run Endpoints (1 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M3.4.1 Preview endpoint | 20-row preview < 60 s on gen-default | 0.5 ew |
| M3.4.2 Run endpoint with SSE | Progress streamed over SSE | 0.3 ew |
| M3.4.3 Cancel endpoint | Graceful shutdown with checkpoint | 0.2 ew |

**Tests:**
- Preview 20 rows → < 60 s
- Cancel → job status `cancelled`

---

## M4.1 Judge Definitions (1.5 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M4.1.1 Pointwise rubric | 1-10 with anchors | 0.5 ew |
| M4.1.2 Pairwise with position swap | Both orders run, agreement recorded | 0.5 ew |
| M4.1.3 Judge registry | Registry with list/get | 0.5 ew |

**Tests:**
- Judge definition → GET returns identical
- 100 rows → position swap (both orders executed)

---

## M4.2 DPO Pair Builder (1.5 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M4.2.1 Margin threshold logic | Low-margin routed to queue | 0.5 ew |
| M4.2.2 Low-margin routing | Appears in annotation queue | 0.5 ew |
| M4.2.3 DPO export format | Loads in TRL DPOTrainer | 0.5 ew |

**Tests:**
- Margin threshold change → different pairs routed
- DPO export → TRL loads and trains 1 step

---

## M5.1 Annotation Queues (2 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M5.1.1 Queue creation with strategies | Round-robin, overlap-k, priority | 0.5 ew |
| M5.1.2 SKIP LOCKED leases | Zero double assignments in load test | 1 ew |
| M5.1.3 TTL-based expiration | Leases return to pool after TTL | 0.5 ew |

**Tests:**
- 50 concurrent annotators → zero double assignments
- Kill worker with active lease → lease expires

---

## M5.2 Annotator UI (4 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M5.2.1 Question types | label, rating, ranking, pairwise, etc. | 1.5 ew |
| M5.2.2 Markdown/code renderer | Full formatting support | 1 ew |
| M5.2.3 Konva canvas | Drag-to-rank, bbox, polygon | 1 ew |
| M5.2.4 Keyboard-first flow | No mouse required for annotation | 0.5 ew |

**Tests:**
- 50 concurrent annotators, p95 < 150 ms
- Keyboard-only flow works

---

## M5.3 Suggestion Display (1 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M5.3.1 Suggestion retrieval | From model/judge | 0.3 ew |
| M5.3.2 Provenance display | Model, score, timestamp visible | 0.3 ew |
| M5.3.3 Accept/edit flow | Both stored | 0.4 ew |

**Tests:**
- Suggestion displayed with provenance
- Accept/edit → final answer stored

---

## M5.4 Lead Dashboard (1 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M5.4.1 Progress metrics | Live counters via SSE | 0.3 ew |
| M5.4.2 Throughput metrics | Requests per second | 0.3 ew |
| M5.4.3 Agreement % | Krippendorff's α, Cohen's κ | 0.4 ew |

**Tests:**
- SSE updates every 5 s
- Metrics match manual calculation

---

## M6.1 Versioning (1.5 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M6.1.1 Draft → version commit | Version immutable | 0.5 ew |
| M6.1.2 Lance version + Postgres row | Manifest hash + stats | 0.5 ew |
| M6.1.3 Tags | Tagged versions marked | 0.5 ew |

**Tests:**
- Re-export → byte-identical
- Tagged version cannot be modified

---

## M6.2 Exporters (2.5 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M6.2.1 JSONL exporter | Valid JSONL format | 0.5 ew |
| M6.2.2 Parquet exporter | Parquet format | 0.5 ew |
| M6.2.3 HF datasets exporter | Loads in datasets.load_dataset | 1 ew |
| M6.2.4 DPO exporter | Loads in TRL DPOTrainer | 0.5 ew |

**Tests:**
- Export 10k rows → format correctness
- DPO export → TRL loads and trains 1 step

---

## M7.1 Langfuse Integration (1 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M7.1.1 Self-hosted Langfuse | Traces recorded | 0.3 ew |
| M7.1.2 LangChain callbacks | Per-run cost aggregated | 0.3 ew |
| M7.1.3 PII redaction hook | PII redacted before trace export | 0.4 ew |

**Tests:**
- Run pipeline → traces created
- Cost aggregation correct

---

## M7.2 Grafana Dashboards (1 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M7.2.1 API dashboard | All metrics visible | 0.2 ew |
| M7.2.2 vLLM dashboard | GPU, latency, throughput | 0.2 ew |
| M7.2.3 Ray dashboard | Worker status | 0.2 ew |
| M7.2.4 GPU dashboard | DCGM metrics | 0.2 ew |
| M7.2.5 Provisioning | Dashboards in Git, Argo-provisioned | 0.2 ew |

**Tests:**
- Dashboard loads in browser
- Panels show data

---

## M7.3 Security Suite (1 ew)

| Task | Acceptance Criteria | Est |
|---|---|---|
| M7.3.1 Cross-tenant access | Tenant A cannot read tenant B | 0.3 ew |
| M7.3.2 CRUD-passthrough lint | No CRUD passthrough endpoints | 0.3 ew |
| M7.3.3 PSA conformance | No privileged containers | 0.2 ew |
| M7.3.4 Secret scan | No secrets in code | 0.2 ew |

**Tests:**
- Cross-tenant access blocked (403)
- No CRUD passthrough in OpenAPI

---

## Testing Strategy

### Unit Tests
- All operators, adapters, pipelines
- Filter DSL parser
- Connector implementations

### Integration Tests
- Database operations
- API endpoints
- End-to-end flows

### Performance Tests
- 1M-record dataset p95 < 200 ms
- 500k import with SSE progress
- 50 concurrent annotators, p95 < 150 ms

### Security Tests
- Cross-tenant isolation
- No secrets in code
- PSA conformance

## Files to Create

```
src/api/
├── core/
│   ├── curation/
│   │   ├── dedup.py
│   │   ├── pii.py
│   │   └── stats.py
│   ├── pipeline/
│   │   ├── spec.py
│   │   ├── compiler.py
│   │   └── checkpointer.py
│   ├── llm/
│   │   ├── litellm_client.py
│   │   ├── route_semaphore.py
│   │   └── response_cache.py
│   ├── judge/
│   │   ├── definition.py
│   │   ├── registry.py
│   │   └── dpo_pair_builder.py
│   ├── annotation/
│   │   ├── queue.py
│   │   └── lease.py
│   └── observability/
│       ├── langfuse.py
│       └── callbacks.py
└── api/v1/endpoints/
    ├── dedup.py
    ├── pii.py
    ├── stats.py
    ├── pipelines.py
    ├── tasks.py
    ├── llm.py
    ├── judges.py
    ├── dpo_pairs.py
    ├── queues.py
    ├── annotations.py
    ├── versions.py
    ├── exports.py
    ├── metrics.py
    └── security.py
```

## Estimated Effort

- M2.2-M2.4: 4 ew
- M3.1-M3.4: 6 ew
- M4.1-M4.2: 3 ew
- M5.1-M5.4: 8 ew
- M6.1-M6.2: 4 ew
- M7.1-M7.3: 3 ew
- **Total: 28 ew**

Plus testing and documentation.
