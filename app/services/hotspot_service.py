from typing import List, Dict

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN


def analyze_occurrences(occurrences: List[Dict]) -> List[Dict]:
    # TODO: Colocar em inglês a docstring
    """
    Recebe uma lista de dicionários com ocorrências, aplica o algoritmo DBSCAN
    para encontrar clusters e retorna a mesma lista com um campo 'cluster' adicionado.

    Args:
        occurrences (List[Dict]): Uma lista de ocorrências, onde cada
                                        ocorrência é um dicionário com pelo menos
                                        as chaves 'latitude' e 'longitude'.

    Returns:
        List[Dict]: A lista de ocorrências processada, com a chave 'cluster'
                    adicionada a cada dicionário.
    """
    if not occurrences:
        return []

    df = pd.DataFrame(occurrences)

    # Garante que as colunas de coordenadas sejam numéricas
    df["latitude"] = pd.to_numeric(df["latitude"])
    df["longitude"] = pd.to_numeric(df["longitude"])

    coords = np.radians(df[["latitude", "longitude"]].values)

    # Parâmetros do DBSCAN
    kms_per_radian = 6371
    epsilon = 1.5 / kms_per_radian  # Raio de 1.5 km
    min_samples = 3  # Mínimo de 3 pontos para formar um cluster

    db = DBSCAN(
        eps=epsilon, min_samples=min_samples, algorithm="ball_tree", metric="haversine"
    ).fit(coords)

    df["cluster"] = db.labels_

    resultado_final = df.to_dict(orient="records")

    return resultado_final
