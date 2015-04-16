class FormRequestMixin(object):

    def get_form_kwargs(self):
        """
        Returns the keyword arguments with the request object for instantiating the form.
        """
        form_kwargs = super(FormRequestMixin, self).get_form_kwargs()
        form_kwargs.update({'request':self.request })
        return form_kwargs
