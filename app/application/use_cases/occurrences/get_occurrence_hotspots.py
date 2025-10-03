from typing import List, Dict

from app.domain.entities.occurrence import Occurrence
from app.domain.repositories.occurrence import OccurrenceGateway
from app.domain.services.hotspot_analysis_service import IHotspotAnalysisService
from app.infrastructure.crossfire.auth import CrossfireAuthService


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
    ) -> List[Dict]:
        """
        Executa a lógica completa de autenticação, busca e análise.
        """
        try:
            access_token = self.auth_service.get_auth_token(email, password)

            if not access_token:
                raise ValueError("Não foi possível obter o token de autenticação.")

            self.occurrence_gateway.set_access_token(access_token)

            occurrences = self.occurrence_gateway.get_occurrences(
                city_name=city_name, state_name=state_name
            )

            analyzed_data = self.analysis_service.analyze_occurrences(occurrences)

            return analyzed_data

        except Exception as e:
            raise e
