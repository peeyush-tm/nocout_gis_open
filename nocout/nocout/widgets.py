from django.forms.widgets import SelectMultiple
from django.forms import ModelChoiceField
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt
# from django.core.exceptions import ValidationError


class MultipleToSingleSelectionWidget(SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html('<select{0}>', flatatt(final_attrs))]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe('\n'.join(output))


class IntReturnModelChoiceField(ModelChoiceField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        '''
        # this code is for getting values as string instead integer
        try:
            key = self.to_field_name or 'pk'
            value = self.queryset.get(**{key:value})
        except (ValueError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        '''
        return value