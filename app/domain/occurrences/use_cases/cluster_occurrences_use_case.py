import numpy as np
import pandas as pd
from app.domain.occurrences.entities.occurrence import Occurrence
from sklearn.cluster import DBSCAN


class ClusterOccurrencesUseCase:

    def __init__(self, epsilon_km: float = 1.5, min_samples: int = 3):
        self.epsilon_km = epsilon_km
        self.min_samples = min_samples

    def execute(self, occurrences: list[Occurrence]) -> list[Occurrence]:
        if not occurrences:
            return []

        df = pd.DataFrame([o for o in occurrences])

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
        epsilon_radians = self.epsilon_km / kms_per_radian

        db = DBSCAN(
            eps=epsilon_radians,
            min_samples=self.min_samples,
            algorithm="ball_tree",
            metric="haversine",
        ).fit(coords_radians)

        df["cluster"] = db.labels_

        return df.to_dict(orient="records")
