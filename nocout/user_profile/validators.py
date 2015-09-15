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
PASSWORD_MIN_LENGTH = getattr(settings, "PASSWORD_MIN_LENGTH", 5)

# Minimum length specified for passwords.
PASSWORD_MAX_LENGTH = getattr(settings, "PASSWORD_MAX_LENGTH", 44)

# Complexity level specified for passwords.
PASSWORD_COMPLEXITY = getattr(settings, "PASSWORD_COMPLEXITY", {'UPPER': 1, 'PUNCTUATION': 1})

# Dictionary word check configuration.
PASSWORD_DICTIONARY = getattr(settings, "PASSWORD_DICTIONARY", {'PATH': '', 'CHECK': False})


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
        if not (self.min_length < len(value) < self.max_length):
            raise ValidationError(
                self.message % _("Must be within %s to %s characters.") % (self.min_length, self.max_length),
                code=self.code)
        else:
            return value


class ComplexityValidator(object):
    """
    Validate complexity level of a string by varifying it corresponding to the minimum
    number of uppercase, digits and punctuation etc. defined in the complexity level specified.
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

        if self.complexities:
            password_set = set(value)

            # Calculate length of uppercase, lowercase, digits and punctuations in password.
            uppercase = set(string.uppercase).intersection(password_set)
            lowercase = set(string.lowercase).intersection(password_set)
            digits = set(string.digits).intersection(password_set)
            punctuation = set(string.punctuation).intersection(password_set)

            # Validate password cases.
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
        else:
            return value


class DictionaryValidator(object):
    """
    Dictionary word validator.
    """
    message = _("Do not use password based on a dictionary word.")
    code = "dictionary_word"

    def __init__(self, dictionary_check):
        self.dictionary_check = dictionary_check

    def __call__(self, value):
        if self.dictionary_check.get('CHECK', False):
            word_dict = {}
            with open(self.dictionary_check.get('PATH', '')) as FileObj:
                for lines in FileObj:
                    word_dict[lines.strip().lower()] = lines.strip().lower()
            if value.strip().lower() in word_dict:
                raise ValidationError(self.message % _("Please do not use dictionary word."), code=self.code)
        else:
            return value


validate_length = LengthValidator(PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH)
complexity = ComplexityValidator(PASSWORD_COMPLEXITY)
validate_dictionary_words = DictionaryValidator(PASSWORD_DICTIONARY)
