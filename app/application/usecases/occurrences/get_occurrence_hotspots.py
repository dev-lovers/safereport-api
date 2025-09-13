from typing import List, Dict

from app.domain.entities.occurrence import Occurrence
from app.domain.repositories.occurrence import OccurrenceGateway
from app.domain.services.hotspot_analysis_service import IHotspotAnalysisService
from app.infrastructure.api_clients.crossfire_auth_service import CrossfireAuthService


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
            # 1. Autenticação e obtenção do token
            access_token = self.auth_service.get_auth_token(email, password)

            if not access_token:
                raise ValueError("Não foi possível obter o token de autenticação.")

            # 2. Configura o gateway de ocorrências com o token
            self.occurrence_gateway.set_access_token(access_token)

            # 3. Usa o gateway para buscar as ocorrências
            occurrences = self.occurrence_gateway.get_occurrences(
                city_name=city_name, state_name=state_name
            )

            # 4. Usa o serviço de análise para processar os dados
            analyzed_data = self.analysis_service.analyze_occurrences(occurrences)

            return analyzed_data

        except Exception as e:
            # Lança a exceção para que a camada de interface a capture
            raise e
