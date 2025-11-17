from fastapi import APIRouter, Depends, Query

from app.domain.places.use_cases.get_suggestions_use_case import GetSuggestionsUseCase
from app.schemas.response import StandardResponse
from app.schemas.suggestion import SuggestionScheme

router = APIRouter(tags=["Places"])


def get_use_case() -> GetSuggestionsUseCase:
    return GetSuggestionsUseCase()


@router.get("/suggestions", response_model=StandardResponse[list[SuggestionScheme]])
async def autocomplete_place(
    query: str = Query(..., description="Termo de busca para sugestões"),
    use_case: GetSuggestionsUseCase = Depends(get_use_case),
):
    suggestions = await use_case.execute(query)
    return StandardResponse(message="Sugestões obtidas com sucesso", data=suggestions)
