def in_group(user=None, group_name=None):
    """
    Check whether user exists in given group or not.
    :param user:
    :return: True/False
    """
    if user and group_name:
        user_groups = set([group.name.lower() for group in user.groups.all()])
        if group_name.lower() in user_groups:
            return True
        else:
            return False
    else:
        return False
