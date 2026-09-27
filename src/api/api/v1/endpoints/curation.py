"""Curation endpoints."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import current_tenant, db

from core.curation.operator import OperatorKind
from core.curation.registry import operator_registry
from core.curation.pipeline import CurationRecipe, CurationPipeline

from api.v1.schemas import (
    OperatorResponse,
    CurationRecipeCreate,
    CurationRecipeResponse,
    CurationRunCreate,
    CurationRunResponse,
)

router = APIRouter()


@router.get("/operators", response_model=List[OperatorResponse])
async def list_operators(
    kind: Optional[OperatorKind] = None,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """List registered operators."""
    operators = operator_registry.list(kind=kind)
    
    return [
        OperatorResponse(
            name=op.name,
            version=op.version,
            kind=op.kind.value,
        )
        for op in operators
    ]


@router.post("/recipes", response_model=CurationRecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_curation_recipe(
    recipe: CurationRecipeCreate,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Create a curation recipe."""
    # TODO: Implement recipe persistence
    return CurationRecipeResponse(
        id=str(uuid.uuid4()),
        name=recipe.name,
        version=recipe.version,
        operators=recipe.operators,
    )


@router.get("/recipes/{recipe_id}", response_model=CurationRecipeResponse)
async def get_curation_recipe(
    recipe_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Get curation recipe by ID."""
    # TODO: Implement recipe retrieval
    return CurationRecipeResponse(
        id=recipe_id,
        name="test_recipe",
        version="1.0",
        operators=[],
    )


@router.post("/recipes/{recipe_id}/runs", response_model=CurationRunResponse)
async def run_curation(
    recipe_id: str,
    run: CurationRunCreate,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Run curation on a dataset."""
    # TODO: Implement recipe retrieval
    recipe = CurationRecipe(
        name="test_recipe",
        version="1.0",
        operators=[],
    )
    
    pipeline = CurationPipeline(recipe)
    result = await pipeline.run(str(run.dataset_id), run.input_version)
    
    return CurationRunResponse(
        id=str(uuid.uuid4()),
        recipe_id=recipe_id,
        dataset_id=str(run.dataset_id),
        status=result["status"],
        input_version=run.input_version,
        stage_stats=result["stage_stats"],
        created_at="2026-09-26T00:00:00Z",
    )


@router.get("/runs/{run_id}", response_model=CurationRunResponse)
async def get_curation_run(
    run_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Get curation run status."""
    # TODO: Implement run status retrieval
    return CurationRunResponse(
        id=run_id,
        recipe_id="test-recipe-id",
        dataset_id="test-dataset-id",
        status="completed",
        stage_stats=[],
        created_at="2026-09-26T00:00:00Z",
    )


@router.get("/runs/{run_id}/results", response_model=CurationRunResponse)
async def get_curation_run_results(
    run_id: str,
    tenant_id: str = Depends(current_tenant),
    session=Depends(db),
):
    """Get curation run results."""
    # TODO: Implement results retrieval
    return CurationRunResponse(
        id=run_id,
        recipe_id="test-recipe-id",
        dataset_id="test-dataset-id",
        status="completed",
        stage_stats=[],
        created_at="2026-09-26T00:00:00Z",
    )
