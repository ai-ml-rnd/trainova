# RESEARCH.md — Market Research: Unified Data Platform for LLM & VLM Training

Status: v1.0 · Date: September 2026 · Companion docs: [ARCHITECTURE.md](ARCHITECTURE.md), [TASK.md](TASK.md)

## Executive Summary

No single product today covers pretraining-corpus curation, synthetic generation, human annotation and preference collection for both text and vision-language (VLM) data. The two open-source tools this project wants to emulate, Argilla and Distilabel, have effectively stopped evolving. This leaves a real, defensible gap for a self-hosted, ARM64-native platform built on FastAPI, Next.js, LangGraph and Deep Agents behind a LiteLLM → vLLM gateway.

- **The gap is real and widening.** Argilla's README now says the original authors have moved on and no new features will be added. Distilabel's last PyPI release dates from January 2025. Lilac was archived in July 2025, and Humanloop was shut down on September 8, 2025. Gretel went to NVIDIA, Galileo to Cisco and Cleanlab to Handshake, while Meta took a 49% stake in Scale AI. What remains is fragmented: curation engines (NeMo Curator, DataTrove, Data-Juicer) have no human UI, annotation tools (Label Studio, CVAT, Encord, Labelbox) have no pretraining curation, and synthetic-data libraries (Data Designer, Bespoke Curator, synthetic-data-kit) have neither.
- **Build an orchestration and UX layer, not a new engine.** Wrap proven Apache-2.0/MIT engines inside one versioned dataset model, one annotation workspace, one LangGraph generation runtime and one Deep Agents "dataset builder", all tenant-scoped behind FastAPI with OIDC and routed through LiteLLM virtual keys. The engines to reuse are DataTrove, NeMo Curator and Data-Juicer operators for curation, Ray for execution and vLLM for generation.
- **DGX GB10 imposes concrete constraints.** The design must be ARM64 everywhere and account for 128 GB of unified CPU/GPU memory with no MIG. The NVIDIA device plugin must be v0.17.4 or later, vLLM needs CUDA-13 builds, and LiteLLM arm64 images come from ghcr.io.

---

## 1. Key Findings

1. **The Argilla/Distilabel era is over as an actively developed stack.** Hugging Face acquired Argilla in 2024. The Argilla README now says the original authors have moved on and no new features will be added, bug fixes only, and it asks for volunteer maintainers. Distilabel (Apache-2.0, ~3.4k stars) still installs, but its latest release, 1.5.3, dates from January 28, 2025. Teams that standardized on this stack now own it.
2. **Consolidation has removed several independent vendors.** NVIDIA acquired Gretel (March 2025, reported nine-figure deal). Databricks absorbed Lilac, and its repo was archived July 25, 2025. Anthropic hired Humanloop's team, and the platform was sunset September 8, 2025. Handshake acqui-hired Cleanlab's research team (January 28, 2026). Cisco completed its Galileo acquisition on May 22, 2026. Meta invested $14.3B for 49% of Scale AI (June 2025); Google and OpenAI then reportedly pulled back from Scale. Syntho acquired the MOSTLY AI brand in June 2026.
3. **Commercial labeling has pivoted to "data-as-a-service."** Snorkel AI moved from selling Snorkel Flow software to delivering finished expert datasets. It raised a $350M Series E at a $3.5B valuation on September 22, 2026. Scale, Labelbox, SuperAnnotate and Handshake all bundle workforce with tooling. Self-hosting, data-sovereign teams are under-served.
4. **Open-source momentum is in curation engines, converging on Ray.** NeMo Curator 26.02 moved to Ray-based pipelines for text, image, video and audio. Version 26.04 made semantic dedup default to vLLM-served embeddings and added a Megatron tokenization writer. Data-Juicer 2.0 ships 150+ operators and a Ray MinHash-LSH deduplicator that handles terabyte-scale data. DataTrove produced FineWeb (18.5T tokens).
5. **Synthetic data has standardized on "LLM endpoint + DAG/columns + judge."** NeMo Data Designer, Bespoke Curator and Meta's synthetic-data-kit all target vLLM and OpenAI-compatible endpoints. None of them has a multi-user human review UI.
6. **Hugging Face is consolidating on vLLM/SGLang.** TGI entered maintenance mode on December 11, 2025. This validates vLLM as the model-in-the-loop engine.
7. **Agent harnesses are now a building block.** LangChain's `deepagents` provides `create_deep_agent` with a planning tool, a virtual filesystem with pluggable backends, subagents, `FilesystemPermission` rules, human-in-the-loop interrupts and MCP tools. Its security model explicitly "trusts the LLM," so boundaries must be enforced at the tool and sandbox level.

---

## 2. Product-by-Product Survey

**Scope legend:**

| Code | Meaning |
|---|---|
| PT | Pretraining curation |
| SFT | Instruction data |
| PREF | Preference data (DPO/RLHF/KTO) |
| SYN | Synthetic generation |
| ANN | Human annotation UI |
| JUDGE | LLM-as-judge |
| MM | Multimodal / VLM |

### 2.1 Annotation and human-feedback tools

| Product | Scope | License / model | Notes |
|---|---|---|---|
| **Argilla** | SFT, PREF, ANN, partial MM | Apache-2.0 | FastAPI server, Vue/Nuxt UI, Postgres + Elasticsearch/OpenSearch. Best LLM feedback schema (fields, questions, suggestions, responses) and HF Hub integration. **Maintenance only**; coarse RBAC. |
| **Label Studio** | ANN, MM, SFT/PREF templates | Apache-2.0 Community + Enterprise | Django + React, ML-backend protocol, XML configs. Most flexible multimodal UI. RBAC/SSO are Enterprise-only. Starter Cloud is $99/month. |
| **CVAT** | ANN (CV: image, video, 3D) | MIT + SaaS | Best open-source bbox/polygon/tracking tool. No LLM preference workflows. |
| **Doccano** | ANN (text) | MIT | Effectively dormant. Not a foundation to build on. |
| **Prodigy** | ANN (NLP), active learning | Commercial, $390+ | Scriptable and fast for one annotator. Not multi-tenant. |
| **Labelbox** | ANN, MM, SFT/PREF, eval | SaaS (LBU usage) | Mature enterprise tool with an expert workforce. Cloud-first, and costs rise at scale. |
| **SuperAnnotate** | ANN, MM, RLHF | SaaS (~$62/user/month) | Closed source, no curation. |
| **Encord** | ANN, MM, RLHF, visual curation | SaaS, quote | Strong on visual data. No web-scale text curation. |
| **V7 Darwin** | ANN, MM (CV/medical) | SaaS, quote | Not LLM-focused. |
| **Scale AI** | Managed labeling, RLHF | Enterprise | Not self-hostable. Vendor-neutrality concerns after the Meta deal. |

### 2.2 LLM-ops, evaluation and data quality

| Product | Status | Lesson |
|---|---|---|
| **Humanloop** | Shut down Sep 2025 | SaaS dependency risk for evaluation data. |
| **Galileo** | Acquired by Cisco (May 2026) | A reference for LLM-as-judge design, not a data tool. |
| **Cleanlab** | Team to Handshake (Jan 2026); library is AGPL-3.0 | Label-quality scoring should be built into the platform. |
| **Lilac** | Archived Jul 2025 | Its cluster/search/filter UX is exactly what curators need, and no maintained OSS equivalent exists. |
| **Snorkel AI** | Pivoted to expert data-as-a-service | Programmatic labeling is proven but closed. |

### 2.3 Pretraining-curation engines

| Engine | Scope | License | Notes |
|---|---|---|---|
| **NVIDIA NeMo Curator** | PT, MM, dedup, classifiers, PII | Apache-2.0 | Ray-based and GPU-accelerated. Library/CLI only. |
| **NeMo Data Designer** | SYN, JUDGE | Apache-2.0 | Column-based configs over vLLM endpoints. **Telemetry is on by default**, so set `NEMO_TELEMETRY_ENABLED=false`. |
| **DataTrove (HF)** | PT (text) | Apache-2.0 | Includes Trafilatura extraction, Gopher/C4/FineWeb filters, fastText lang ID, MinHash (5-grams, 14×8) and PII. SLURM-oriented. |
| **Dolma toolkit (AI2)** | PT (text) | Apache-2.0 | Taggers, Bloom-filter dedup and mixing. Development has slowed. |
| **Data-Juicer** | PT, SFT, MM | Apache-2.0 | 150+ operators across Ray, REST API and web UI. No multi-user annotation. |
| **DatologyAI** | PT curation as a service | Commercial | Proves demand for curation as a product, but it isn't self-serve. |
| **Unstructured** | Document ingestion | Apache-2.0 + SaaS | The OSS library lags the hosted API. Disable its analytics. |

### 2.4 Synthetic data generators

| Tool | License | Notes |
|---|---|---|
| **Distilabel** | Apache-2.0 | Step/Task DAGs with caching and vLLM/LiteLLM backends. Stagnant since early 2025. |
| **Bespoke Curator** | Apache-2.0 | Structured outputs, caching, batch APIs and a LiteLLM/vLLM backend. Used for OpenThoughts and Bespoke-Stratos. |
| **synthetic-data-kit (Meta)** | Unclear, verify | Document → QA/CoT with judge curation (threshold 7.0) and Lance storage. |
| **Gretel** | Now part of NVIDIA | No longer independent. |
| **MOSTLY AI SDK** | Apache-2.0 | Tabular data. Stewardship is uncertain after the Syntho brand sale. |
| **CuratorKIT (arXiv 2026)** | Research | Useful reference for append-only per-sample provenance. |

### 2.5 Training-side tooling

**HF `datasets`** (Apache-2.0) is the lingua franca for exports. **AutoTrain** is a no-code fine-tuning front end. Treat both as export sinks, not competitors.

---

## 3. Comparison Matrix

| Product | PT | SFT | PREF | SYN | ANN | JUDGE | MM | Self-host | License | 2025–26 status |
|---|---|---|---|---|---|---|---|---|---|---|
| Argilla | – | ✓ | ✓ | – | ✓ | via Distilabel | partial | ✓ | Apache-2.0 | Maintenance only |
| Distilabel | – | ✓ | ✓ | ✓ | – | ✓ | partial | ✓ | Apache-2.0 | Stagnant |
| Label Studio | – | ✓ | ✓ | – | ✓ | Ent. | ✓ | ✓ | Apache-2.0 + Ent. | Active |
| CVAT | – | – | – | – | ✓ (CV) | – | ✓ | ✓ | MIT + SaaS | Active |
| Doccano | – | partial | – | – | ✓ | – | – | ✓ | MIT | Dormant |
| Prodigy | – | ✓ | partial | – | ✓ | partial | partial | ✓ | Commercial | Active, small |
| Labelbox | – | ✓ | ✓ | – | ✓ | ✓ | ✓ | limited | SaaS | Active |
| SuperAnnotate | – | ✓ | ✓ | – | ✓ | ✓ | ✓ | limited | SaaS | Active |
| Encord | partial | ✓ | ✓ | – | ✓ | ✓ | ✓ | limited | SaaS | Active |
| V7 Darwin | – | partial | – | – | ✓ | partial | ✓ | limited | SaaS | Active |
| Scale AI | – | ✓ | ✓ | – | managed | ✓ | ✓ | – | Enterprise | Meta 49% |
| Snorkel | – | ✓ | ✓ | ✓ | programmatic | ✓ | partial | Ent. | Commercial | Pivoted to DaaS |
| Humanloop | – | – | – | – | feedback | ✓ | – | – | SaaS | Shut down |
| Galileo | – | – | – | – | – | ✓ | – | Ent. | Commercial | Cisco/Splunk |
| Cleanlab | – | label QA | – | – | – | ✓ | partial | lib | AGPL + SaaS | Handshake |
| Lilac | explore | explore | – | – | light | – | – | ✓ | Apache-2.0 | Archived |
| NeMo Curator | ✓ | partial | – | via NDD | – | classifiers | ✓ | ✓ | Apache-2.0 | Very active |
| NeMo Data Designer | – | ✓ | ✓ | ✓ | – | ✓ | partial | ✓ | Apache-2.0 | Active |
| DataTrove | ✓ | – | – | – | – | – | – | ✓ | Apache-2.0 | Active |
| Dolma toolkit | ✓ | – | – | – | – | – | – | ✓ | Apache-2.0 | Slow |
| Data-Juicer | ✓ | ✓ | partial | partial | – | partial | ✓ | ✓ | Apache-2.0 | Active |
| synthetic-data-kit | – | ✓ | – | ✓ | – | ✓ | partial | ✓ | Unclear | Active |
| Bespoke Curator | – | ✓ | partial | ✓ | viewer | ✓ | partial | ✓ | Apache-2.0 | Active |
| Unstructured | ingest | ingest | – | – | – | – | docs | ✓ | Apache-2.0 + SaaS | Active |
| DatologyAI | ✓ | ✓ | – | ✓ | – | – | ✓ | in-VPC | Commercial | Active |
| **Proposed platform (Forge)** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ ARM64 | Internal / OSS-able | — |

---

## 4. The Market Gap

**What no one offers:** a single self-hostable system where one versioned dataset flows through every stage, with provenance for every record and decision:

1. Raw crawl or document ingestion.
2. Dedup, quality and PII curation.
3. Agent-planned synthetic expansion using local vLLM models.
4. LLM-as-judge scoring.
5. Human review of the uncertain slice, for text **and** image/bbox/VQA.
6. Preference pairs.
7. Versioned export to training formats.

**Why now:**
- The leading OSS feedback stack is orphaned.
- Vendors are consolidating into frontier-lab data services that don't suit on-prem teams.
- The building blocks have matured in 2025–2026: Ray-native curation, vLLM, LiteLLM, LangGraph durability and Deep Agents.

**Positioning for BLP Industry.ai:** an "Argilla + Distilabel + Lilac + Curator-UI" successor that runs on DGX GB10/k3s. Its differentiators are:
1. One record model spanning pretraining and post-training.
2. Agentic dataset building with human approval gates.
3. ARM64 and unified-memory-aware operations.
4. Compliance-grade provenance.

**Build vs. buy verdict:**
- **Build** the platform layer.
- **Reuse** DataTrove/NeMo Curator/Data-Juicer operators, Ray, vLLM, LiteLLM, Langfuse and HF `datasets`.
- **Do not fork Argilla.** Its maintenance status and Vue/Elasticsearch stack conflict with the Next.js requirement. Borrow its schema concepts instead.

---

## 5. Caveats

- Third-party pricing (SuperAnnotate, CVAT tiers, Snorkel estimates, V7) comes from review sites and is indicative only.
- Some 2026 status claims rest on single or secondary sources. These include the Galileo → Splunk rename, Scale AI leadership changes, Snorkel's run-rate and the LiteLLM Docker Hub amd64-only report.
- Not independently verified:
  - HF AutoTrain's 2026 maintenance status.
  - synthetic-data-kit's license.
  - Current MinIO community distribution terms.
  - Arm64 availability of the exact Langfuse, Keycloak and CloudNativePG versions you plan to deploy.

  Validate these in Phase 0 (see TASK.md F1.5, F2.2).
- GB10 performance guidance comes from practitioner write-ups, not NVIDIA benchmarks. Confirm it with your own load tests.
