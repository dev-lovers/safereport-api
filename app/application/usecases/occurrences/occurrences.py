from app.domain.repositories import OccurrenceGateway
from app.domain.entities import Occurrence
from app.infrastructure.api_clients.crossfire_auth_service import CrossfireAuthService
from app.domain.services import IHotspotAnalysisService


class GetOccurrencesUseCase:
    def __init__(self, occurrence_gateway: OccurrenceGateway):
        self.occurrence_gateway = occurrence_gateway

    def execute(self, city_id: str, state_id: str) -> list[Occurrence]:
        return self.occurrence_gateway.get_occurrences(city_id, state_id)


class GetOccurrenceHotspotsUseCase:
    """
    Caso de uso para obter e analisar hotspots de ocorrências.
    """

    def __init__(
        self,
        auth_service: CrossfireAuthService,
        occurrence_gateway: OccurrenceGateway,
        analysis_service: IHotspotAnalysisService,
    ):
        self.auth_service = auth_service
        self.occurrence_gateway = occurrence_gateway
        self.analysis_service = analysis_service

    def execute(
        self, email: str, password: str, city_name: str, state_name: str
    ) -> list[dict]:
        access_token = self.auth_service.get_auth_token(email, password)
        if not access_token:
            raise ValueError("Não foi possível obter o token de autenticação.")

        self.occurrence_gateway.set_access_token(access_token)

        occurrences = self.occurrence_gateway.get_occurrences(
            city_name=city_name, state_name=state_name
        )

        analyzed_data = self.analysis_service.analyze_occurrences(occurrences)

        return analyzed_data
