# Phase 2 (v1) Implementation Plan

## Overview

Phase 2 expands the MVP with multimodal (VLM) support, deep agent dataset building, scale-out curation, annotation quality, and advanced versioning.

## Tasks

### V1.1 Multimodal (VLM) Data — 9 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| V1.1 | Image fields: content-addressed upload, thumbnails, EXIF stripping, pHash dedup | Duplicate uploads stored once | 1.5 ew |
| V1.2 | Konva canvas: bbox, polygon, keypoints; VQA (optional region grounding); caption edit; image-grounded pairwise | 500 boxes on a 4K image at 60 fps; exports COCO-style and LLaVA conversations | 4 ew |
| V1.3 | VLM tasks: captioning, VQA generation, image-grounded preference via `vlm-default`; VLM judge | Preview works end to end on VLM route | 2 ew |
| V1.4 | Image curation ops: CLIP-score, resolution/aspect, NSFW | Rejections carry reasons | 1.5 ew |

### V2.1 Deep Agents Dataset Builder — 7 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| V2.1 | `create_deep_agent` service: composite FS (Store namespaced by tenant/session), deny-by-default `FilesystemPermission`, typed tools, per-session budget | Red-team: no cross-tenant reads, no non-allow-listed tools, budget enforced | 3 ew |
| V2.2 | Subagents: schema-designer, prompt-engineer, quality-analyst, curation-planner | Valid spec + 20-row preview within 10 min for 4 of 5 benchmark briefs | 2 ew |
| V2.3 | HITL UI: plan view, spec diff, approve/reject interrupts, streamed tool calls | No side-effecting tool runs without an approval record in audit | 2 ew |

### V3.1 Scale-out Curation — 6 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| V3.1 | KubeRay autoscaling (CPU + GPU pools), GCS fault tolerance | Head-pod kill recovers running job | 1.5 ew |
| V3.2 | Distributed MinHash with union-find on Ray actors; WARC + Trafilatura at scale | 1 TB text deduplicated end to end with documented throughput; resumable | 2.5 ew |
| V3.3 | Semantic dedup (vLLM embeddings + k-means) and model quality classifiers | Configurable thresholds; stats per cluster | 2 ew |

### V4.1 Annotation Quality — 4 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| V4.1 | Gold/honeypot items, Krippendorff's α / Cohen's κ, per-annotator accuracy | Metrics on dashboard | 1.5 ew |
| V4.2 | Reviewer adjudication and consensus resolution | Adjudicated value becomes canonical response | 1.5 ew |
| V4.3 | Judge calibration vs human labels; "calibrated judges only" export policy | Judge with κ below threshold cannot gate export | 1 ew |

### V5.1 Versioning & Export v1 — 3 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| V5.1 | Branches, two-parent merges and a row-level diff UI | Branches track parent commits; merge shows diff | 1.5 ew |
| V5.2 | Export policies (license, PII-clean, judge calibration) and WebDataset shards | Policy enforcement in exporter; WebDataset format working | 1.5 ew |

### V6.1 Ingestion v1 — 3 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| V6.1 | Polite URL crawler (robots.txt, per-domain rate limits, license/opt-out tags) | 1.5 ew |
| V6.2 | Document parsing (Unstructured OSS with analytics off, pdfium fast path) and VLM OCR for scans | 1.5 ew |

### V7.1 RBAC & Ops Hardening — 3 ew

| ID | Task | Acceptance Criteria | Est |
|---|---|---|---|
| V7.1 | Cerbos/OPA policy engine with ARCHITECTURE §10 roles, plus dataset sensitivity labels | 1.5 ew |
| V7.2 | Backups (CNPG WAL, bucket versioning, Velero), restore drill, runbooks | RPO ≤ 15 min, RTO ≤ 4 h in drill | 1.5 ew |

## Total Effort

- **Phase 2 (v1):** 35 ew

## Files to Create

```
src/api/
├── core/
│   ├── multimodal/
│   │   ├── image_store.py
│   │   ├── image_curation.py
│   │   └── vlm_tasks.py
│   ├── deep_agents/
│   │   ├── agent_service.py
│   │   ├── subagents.py
│   │   └── hitl_ui.py
│   ├── ray_curation/
│   │   ├── distributed_dedup.py
│   │   ├── semantic_dedup.py
│   │   └── ray_executor.py
│   ├── annotation_quality/
│   │   ├── metrics.py
│   │   ├── adjudication.py
│   │   └── judge_calibration.py
│   └── rbac/
│       ├── cerbos_client.py
│       └── policy_engine.py
└── api/v1/endpoints/
    ├── images.py
    ├── vlm_tasks.py
    ├── deep_agents.py
    ├── ray_curation.py
    ├── annotation_quality.py
    ├── branches.py
    ├── export_policies.py
    ├── ingestion.py
    └── rbac.py
```

## Next Steps

1. Implement V1.1: Multimodal image fields
2. Implement V1.2: Konva canvas with VLM support
3. Implement V1.3: VLM tasks and judges
4. Implement V1.4: Image curation ops
