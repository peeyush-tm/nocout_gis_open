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


def display_time(seconds, granularity=4):
        """

        :param seconds: seconds on float
        :param granularity:
        :return:
        """
        intervals = (
            ('weeks', 604800),
            ('days', 86400),
            ('hours', 3600),
            ('minutes', 60),
            ('seconds', 1),
        )
        result = []
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])