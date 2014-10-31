import os
from django.core.exceptions import ValidationError
from django import forms
from nocout.widgets import IntReturnModelChoiceField
from devicevisualization.models import KMZReport
from django.forms.util import ErrorList
import logging
logger = logging.getLogger(__name__)



class KmzReportForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(KmzReportForm, self).__init__(*args, **kwargs)

        try:
            if 'instance' in kwargs:
                self.id = kwargs['instance'].id
        except Exception as e:
            logger.info(e.message)

        for name, field in self.fields.items():
            if field.widget.attrs.has_key('class'):
            	if not(isinstance(field.widget, forms.widgets.CheckboxInput)):
	                field.widget.attrs['class'] += ' tip-focus form-control'
	                field.widget.attrs['data-toggle'] = 'tooltip'
	                field.widget.attrs['data-placement'] = 'right'
	                field.widget.attrs['title'] = field.help_text
	                field.widget.attrs['style'] = 'padding:0px 12px;height:40px;'
                else:
                	field.widget.attrs['checked'] = "true"
            else:
            	if not(isinstance(field.widget, forms.widgets.CheckboxInput)):
	                field.widget.attrs.update({'class': ' tip-focus form-control'})
	                field.widget.attrs.update({'data-toggle': 'tooltip'})
	                field.widget.attrs.update({'data-placement': 'right'})
	                field.widget.attrs.update({'title': field.help_text})
	                field.widget.attrs.update({'style' : 'padding:0px 12px;height:40px;'})
                else:
                	field.widget.attrs['checked'] = "true"

    class Meta:
        """
        Meta Information
        """
        model = KMZReport
        exclude = ['added_on', 'user']

    def clean_file_name(self):
        IMPORT_FILE_TYPES = ['.kmz', '.kml']
        input_kmz = self.cleaned_data.get('filename')
        extension = os.path.splitext(input_kmz.name)[1]
        if not (extension in IMPORT_FILE_TYPES):
            raise ValidationError( u'%s is not the supported file. Please make sure your input file is an KMZ(.kmz) file.' % extension )
        else:
            return input_kmz

    def clean_name(self):
        """
        Name unique validation
        """
        name = self.cleaned_data['name']
        names = KMZReport.objects.filter(name=name)
        try:
            if self.id:
                names = names.exclude(pk=self.id)
        except Exception as e:
            logger.info(e.message)
        if names.count() > 0:
            raise ValidationError('This name is already in use.')
        
        return name