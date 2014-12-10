"""
Provide custom validations for password input.
"""

from __future__ import division
import string

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.conf import settings


# Settings
PASSWORD_MIN_LENGTH = getattr(settings, "PASSWORD_MIN_LENGTH", 6)
PASSWORD_COMPLEXITY = getattr(settings, "PASSWORD_COMPLEXITY", {'UPPER': 1, 'LOWER': 1, 'DIGIT': 1})


class LengthValidator(object):
    message = _("Invalid Length (%s)")
    code = "length"

    def __init__(self, min_length=None, max_length=None):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        if self.min_length and len(value) < self.min_length:
            raise ValidationError(
                self.message % _("Must be %s characters or more") % self.min_length,
                code=self.code)


class ComplexityValidator(object):
    message = _("Password must  contain (%s)")
    code = "complexity"

    def __init__(self, complexities):
        self.complexities = complexities

    def __call__(self, value):
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
