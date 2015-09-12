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
from user_profile.validators import validate_length, complexity, validate_dictionary_words


class PasswordField(CharField):
    """
    Provide password field for custom validations.

    Validation Types:
      1. Minimum Length
      2. Complexity
    """
    default_validators = [validate_length, complexity, validate_dictionary_words]

    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = PasswordInput(render_value=False)

        super(PasswordField, self).__init__(*args, **kwargs)
