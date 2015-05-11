"""
======================================================
Module contains custom validations for password input.
======================================================

Location:
* /nocout_gis/nocout/user_profile/validators.py

List of constructs:
=======
Classes
=======
* UserList
* UserListingTable
* UserArchivedListingTable
* UserDetail
* UserCreate
* UserUpdate
* UserDelete
* CurrentUserProfileUpdate

=======
Methods
=======
* organisation_user_list
* organisation_user_select
* change_password
"""


from __future__ import division
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import string


# Minimum length specified for passwords.
PASSWORD_MIN_LENGTH = getattr(settings, "PASSWORD_MIN_LENGTH", 6)

# Complexity level specified for passwords.
PASSWORD_COMPLEXITY = getattr(settings, "PASSWORD_COMPLEXITY", {'UPPER': 1, 'LOWER': 1, 'DIGIT': 1})


class LengthValidator(object):
    """
    Validate length of a string.

    Take two parameters during initialization.
    For e.g., len_obj = LengthValidator(2, 8)
    Following are the parameters passed during initialization:
    1. min_length - Minimum length for string.
    2. max_length - Maximum length for string.

    Take one parameter on calling object as a function.
    For e.g., len_obj('pass1234')
    Following are the parameters passed during function call operator:
    1. value - String which needs to be validated.
    """
    message = _("Invalid Length (%s)")
    code = "length"

    def __init__(self, min_length=None, max_length=None):
        """
        Initialize instance with min and max length settings.
        """
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        """
        Make instance callable as a function without impacting the lifecycle of the object.
        Modify internal state of the instance.
        """
        if self.min_length and len(value) < self.min_length:
            raise ValidationError(
                self.message % _("Must be %s characters or more") % self.min_length,
                code=self.code)


class ComplexityValidator(object):
    """
    Validate complexity level of a string by varifying it corresponding to the minimum
    number of uppercase, digits and punctuation etc. defined in the complexity level specified.

    Take one parameter during initialization.
    For e.g., com_obj = ComplexityValidator({'UPPER': 1, 'LOWER': 1, 'DIGIT': 1})
    Following are the parameters passed during initialization:
    1. complexities - Dictionary object containing complexity level info.

    Take one parameter on calling object as a function.
    For e.g., com_obj('pass1234')
    Following are the parameters passed during function call operator:
    1. value - String which needs to be validated.
    """
    message = _("Password must  contain (%s)")
    code = "complexity"

    def __init__(self, complexities):
        """
        Initialize instance with complexity level settings.
        """
        self.complexities = complexities

    def __call__(self, value):
        """
        Make instance callable as a function without impacting the lifecycle of the object.
        Modify internal state of the instance.
        """
        if self.complexities is None:
            return

        uppercase, lowercase, digits, punctuation = set(), set(), set(), set()

        for character in value:
            if character.isupper():
                uppercase.add(character)
            elif character.islower():
                lowercase.add(character)
            elif character.isdigit():
                digits.add(character)
            elif character in string.punctuation:
                punctuation.add(character)

        if len(uppercase) < self.complexities.get("UPPER", 0):
            raise ValidationError(
                self.message % _(" %(UPPER)s or more uppercase characters") % self.complexities,
                code=self.code)
        elif len(lowercase) < self.complexities.get("LOWER", 0):
            raise ValidationError(
                self.message % _(" %(LOWER)s or more lowercase characters") % self.complexities,
                code=self.code)
        elif len(digits) < self.complexities.get("DIGITS", 0):
            raise ValidationError(
                self.message % _(" %(DIGITS)s or more digits") % self.complexities,
                code=self.code)
        elif len(punctuation) < self.complexities.get("PUNCTUATION", 0):
            raise ValidationError(
                self.message % _(" %(PUNCTUATION)s or more special character") % self.complexities,
                code=self.code)


validate_length = LengthValidator(PASSWORD_MIN_LENGTH)
complexity = ComplexityValidator(PASSWORD_COMPLEXITY)
