def validate_coordinates(latitude, longitude):
    """
    Valida se a latitude e longitude estão dentro dos limites geográficos.

    Args:
        latitude (float): O valor da latitude a ser validado.
        longitude (float): O valor da longitude a ser validado.

    Returns:
        bool: True se as coordenadas forem válidas, False caso contrário.
    """
    if -90 <= latitude <= 90 and -180 <= longitude <= 180:
        return True
    else:
        return False
