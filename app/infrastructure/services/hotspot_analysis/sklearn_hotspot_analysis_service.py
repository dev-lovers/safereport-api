from typing import Dict

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

from app.domain.services.hotspot_analysis_service import IHotspotAnalysisService


class SklearnIHotspotAnalysisService(IHotspotAnalysisService):
    """
    Implementação concreta de IHotspotAnalysisService usando scikit-learn.
    """

    def analyze_occurrences(self, occurrences: list[Dict]) -> list[Dict]:
        if not occurrences:
            return []

        df = pd.DataFrame(occurrences)

        # O seu código de análise assume as chaves latitude e longitude.
        # Vamos garantir que elas existam.
        df["latitude"] = pd.to_numeric(df.get("latitude", 0))
        df["longitude"] = pd.to_numeric(df.get("longitude", 0))

        coords = np.radians(df[["latitude", "longitude"]].values)

        kms_per_radian = 6371
        epsilon = 1.5 / kms_per_radian
        min_samples = 3

        db = DBSCAN(
            eps=epsilon,
            min_samples=min_samples,
            algorithm="ball_tree",
            metric="haversine",
        ).fit(coords)

        df["cluster"] = db.labels_

        resultado_final = df.to_dict(orient="records")

        return resultado_final
