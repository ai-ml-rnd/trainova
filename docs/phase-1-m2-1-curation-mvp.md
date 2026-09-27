# Phase 1 M2.1 Curation MVP Implementation Plan

## Overview

Implement curation pipeline operators for data quality, deduplication, and filtering.

## Requirements

From tasks.md:
- Operator interface + registry
- DataTrove filter adapters (Gopher, C4, FineWeb)
- fastText lang ID / GlotLID integration
- Every rejected row has `reject_reason`
- Per-stage stats

## Architecture

### Operator Interface

```python
class Operator(Protocol):
    name: str
    version: str
    kind: Literal["mapper", "filter", "dedup", "tagger", "stats"]
    
    def process_batch(
        self, batch: pa.RecordBatch, ctx: OpContext
    ) -> pa.RecordBatch:
        """Process a batch, return transformed batch."""
        pass
```

### Operator Kinds

- **mapper**: Adds/modifies columns (lang ID, quality score)
- **filter**: Removes rows (quality filters, toxicity filters)
- **dedup**: Identifies duplicates (exact, fuzzy, semantic)
- **tagger**: Tags rows (PII, NSFW)
- **stats**: Computes statistics (token counts, length histograms)

### Curation Recipe

A sequence of operators applied to a dataset:

```yaml
name: basic_curation
version: "1.0"
operators:
  - name: lang_id
    kind: tagger
    config: {model: "lid.176", threshold: 0.65}
  - name: quality_filter
    kind: filter
    config: {policy: "fineweb", threshold: 0.5}
  - name: exact_dedup
    kind: dedup
    config: {}
```

## Implementation Plan

### 1. Operator Registry

```python
class OperatorRegistry:
    def register(operator: Operator) -> None
    def get(name: str, version: Optional[str] = None) -> Operator
    def list() -> List[Operator]
```

### 2. Operator Implementations

#### Language ID Operator
- fastText lid.176 or GlotLID
- Configurable threshold
- Adds `lang` and `lang_score` columns

#### Quality Filter Operator
- Gopher, C4, FineWeb filter families
- Configurable thresholds
- Rejection reasons stored in `reject_reason`

#### PII Operator
- Presidio + regex
- Tag/redact/hash/replace options
- Encrypted redaction map storage

#### Exact Dedup Operator
- SHA-256 hash of normalized text
- Cluster IDs stored

### 3. Operator Adapter Pattern

```python
class DataTroveAdapter(Operator):
    """Adapter for DataTrove operators."""
    
    def __init__(self, dt_operator):
        self.dt_operator = dt_operator
    
    def process_batch(self, batch, ctx):
        # Convert Arrow batch to DataTrove format
        dt_batch = self._to_datatrove(batch)
        # Process
        result = self.dt_operator.process(dt_batch)
        # Convert back to Arrow
        return self._to_arrow(result)
```

### 4. Pipeline Execution

```python
class CurationPipeline:
    def __init__(self, recipe: CurationRecipe):
        self.operators = [registry.get(op.name, op.version) for op in recipe.operators]
    
    async def run(self, dataset_id: str) -> CurationResult:
        # Load dataset
        # Apply each operator
        # Save results
        # Return stats
```

## API Endpoints

```python
POST /v1/curation-recipes
  - Create curation recipe
  - Request: {name, version, operators: [...]}

GET /v1/curation-recipes/{id}
  - Get recipe by ID

POST /v1/curation-recipes/{id}/runs
  - Run curation on dataset
  - Request: {dataset_id: "...", input_version: 1}

GET /v1/curation-runs/{id}
  - Get run status

GET /v1/curation-runs/{id}/results
  - Get results with stats
```

## Testing Strategy

1. Apply operator to 100k rows
2. Verify rejections have `reject_reason`
3. Per-stage stats correct
4. Resumability (kill + resume)

## Files to Create

```
src/api/
├── core/
│   └── curation/
│       ├── __init__.py
│       ├── operator.py          # Operator interface
│       ├── registry.py          # Operator registry
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── datatrove.py     # DataTrove adapters
│       │   └── fasttext.py      # fastText adapter
│       └── pipeline.py          # Curation pipeline
└── api/v1/endpoints/
    └── curation.py
```

## Dependencies

- `fasttext` or `glotlid` for language ID
- `datatrove` for filters (Apache-2.0)
- `presidio` for PII detection
