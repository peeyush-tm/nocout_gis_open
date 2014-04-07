from django.forms.widgets import SelectMultiple
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt

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