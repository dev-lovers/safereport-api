from fastapi import APIRouter, HTTPException, Depends, Query

from app.infrastructure.api_clients.autocomplete_service import AutocompleteService

router = APIRouter(tags=["Places"])


def get_autocomplete_service() -> AutocompleteService:
    return AutocompleteService()


@router.get("/suggestions")
async def autocomplete_place(
        query: str = Query(..., description="Termo de busca para sugestões de lugares"),
        autocomplete_service: AutocompleteService = Depends(get_autocomplete_service),
):
    try:
        return autocomplete_service.get_suggestions(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
