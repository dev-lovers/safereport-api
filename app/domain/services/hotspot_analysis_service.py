from abc import ABC, abstractmethod


class IHotspotAnalysisService(ABC):

    @abstractmethod
    def analyze_occurrences(self, occurrences: list[dict]) -> list[dict]:
        pass
