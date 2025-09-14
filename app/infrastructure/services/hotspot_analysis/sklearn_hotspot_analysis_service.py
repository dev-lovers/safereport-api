from typing import Dict, List

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

# Apenas para ilustração, não é necessário na implementação real
# from app.domain.services.hotspot_analysis_service import IHotspotAnalysisService


class SklearnIHotspotAnalysisService:  # A classe é mantida para exemplo

    def analyze_occurrences(self, occurrences: List[Dict]) -> List[Dict]:
        if not occurrences:
            return []

        df = pd.DataFrame(occurrences)

        required_columns = ["latitude", "longitude"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"As colunas {required_columns} são obrigatórias.")

        for col in required_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(subset=required_columns, inplace=True)
        if df.empty:
            return []

        coords_radians = np.radians(df[["latitude", "longitude"]].values)
        kms_per_radian = 6371.0

        epsilon_km = 1.5
        epsilon_radians = epsilon_km / kms_per_radian
        min_samples = 3

        db = DBSCAN(
            eps=epsilon_radians,
            min_samples=min_samples,
            algorithm="ball_tree",
            metric="haversine",
        ).fit(coords_radians)

        df["cluster"] = db.labels_

        return df.to_dict(orient="records")
