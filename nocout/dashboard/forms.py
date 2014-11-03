from django import forms

from dashboard.models import DashboardSetting

import logging
logger = logging.getLogger(__name__)


class DashboardSettingForm(forms.ModelForm):
    """
    Rendering form for Dashboard Settings.
    """
    def __init__(self, *args, **kwargs):

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        super(DashboardSettingForm, self).__init__(*args, **kwargs)
        for i in range(1, 11):
            self.fields['range%d_color_hex_value' %i].widget.attrs.update({'class':'colorpicker',\
                                                            'data-color-format':'rgba' })
        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class':'form-control'})

    class Meta:
        """
        Meta Information
        """
        model = DashboardSetting
