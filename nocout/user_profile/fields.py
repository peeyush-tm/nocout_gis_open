"""
===============================================================================
Module contains custom fields required in forms specific to 'user_profile' app.
===============================================================================

Location:
* /nocout_gis/nocout/user_profile/fields.py

List of constructs:
=======
Classes
=======
* PasswordField
"""

from django.forms import CharField, PasswordInput
from user_profile.validators import validate_length, complexity


class PasswordField(CharField):
    """
    Provide password field for custom validations.

    Validation Types:
      - Minimum Length
      - Complexity
    """
    default_validators = [validate_length, complexity]

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key("widget"):
            kwargs["widget"] = PasswordInput(render_value=False)

        super(PasswordField, self).__init__(*args, **kwargs)