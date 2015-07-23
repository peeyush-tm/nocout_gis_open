from django.forms.widgets import SelectMultiple
from django.forms import ModelChoiceField
from django.utils.encoding import force_text
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

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)

        try:
            selected_choices = eval(list(selected_choices)[0])
        except Exception as e:
            pass

        temp_selection_choices = list()

        if not isinstance(selected_choices, list):
            temp_selection_choices.append(unicode(selected_choices))
            selected_choices = temp_selection_choices

        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''

        return format_html('<option value="{0}"{1}>{2}</option>',
                           option_value,
                           selected_html,
                           force_text(option_label))


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