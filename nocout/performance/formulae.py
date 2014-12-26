"""
Store formulae for service.ServiceDataSource.
"""

def rta_null(rta=0):
    """

    :param rta:
    :return:
    """
    try:
        if float(rta) == 0:
            return None
    except Exception as e:
        return None

    return rta
