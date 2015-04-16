from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from dashboard.models import DashboardSetting, MFRDFRReports

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
        self.fields['technology'].choices = [(2, 'P2P'), (4, 'PMP'), (3, 'WiMAX'), ('', 'All')]
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


class MFRDFRReportsForm(forms.ModelForm):
    """
    Render and validate form for MFRDFRReports.
    """

    def __init__(self, *args, **kwargs):
        super(MFRDFRReportsForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs['class'] += ' col-md-12'
                    field.widget.attrs['class'] += ' select2select'
                else:
                    field.widget.attrs['class'] += ' form-control'
            else:
                if isinstance(field.widget, forms.widgets.Select):
                    field.widget.attrs.update({'class': 'col-md-12 select2select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = MFRDFRReports
        fields = ('name', 'type', 'process_for', 'upload_to')

    def clean_process_for(self):
        """
        DFR: Unique for a day.
        MFR: Unique for a month.
        """
        process_for = self.cleaned_data['process_for']
        if 'type' in self.cleaned_data:
            report_type = self.cleaned_data['type']
        else:
            return process_for
        if process_for is None:
            process_for = timezone.now()

        if report_type == 'DFR' and MFRDFRReports.objects.filter(process_for=process_for, type='DFR').exists():
            raise ValidationError('Report for this date already exists.')
        elif report_type == 'MFR' and MFRDFRReports.objects.filter(process_for__year=process_for.year,
                process_for__month=process_for.month, type='MFR').exists():
            raise ValidationError('Report for this month already exists.')

        return process_for
