from actstream.models import Action
from django.db import models
from django.utils.translation import ugettext as _
# from activity_stream.actions import action_handler
from actstream.signals import action
from actstream import settings as actstream_settings

import datetime
from actstream import settings
from actstream.exceptions import check_actionable_model
from django.contrib.contenttypes.models import ContentType

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.datetime.now

class ActivityStreamAction(Action):

    # def __unicode__(self):
    #     ctx = {
    #     'actor': self.actor,
    #     'verb': self.verb,
    #     'action_object': self.action_object,
    #     'target': self.target,
    #     'timesince': self.timesince()
    # }
    #
    #     if self.target:
    #         ctx.update(dict(target_class=self.target.__class__.__name__))
    #         if self.action_object:
    #             ctx.update(dict(action_object_class=self.action_object.__class__.__name__))
    #             return _('%(actor)s %(verb)s %(action_object)s %(action_object_class)s on %(target)s %(target_class)s %(timesince)s ago') % ctx
    #         return _('%(actor)s %(verb)s %(target)s %(target_class)s %(timesince)s ago') % ctx
    #     if self.action_object:
    #         ctx.update(dict(action_object_class=self.action_object.__class__.__name__))
    #         return _('%(actor)s %(verb)s %(action_object)s %(action_object_class)s %(timesince)s ago') % ctx
    #     return _('%(actor)s %(verb)s %(timesince)s ago') % ctx
    action_string=models.CharField(max_length=50)
    objects = actstream_settings.get_action_manager()


    def __unicode__(self):
        super(ActivityStreamAction, self).__unicode__()

def action_handler(verb, **kwargs):
    """
    Handler function to create Action instance upon action signal call.
    """
    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')
    check_actionable_model(actor)

    # We must store the unstranslated string
    # If verb is an ugettext_lazyed string, fetch the original string
    if hasattr(verb, '_proxy____args'):
        verb = verb._proxy____args[0]


    # newaction = ActivityStreamAction(
    #     actor_content_type=ContentType.objects.get_for_model(actor),
    #     actor_object_id=actor.pk,
    #     verb=unicode(verb),
    #     public=bool(kwargs.pop('public', True)),
    #     description=kwargs.pop('description', None),
    #     timestamp=kwargs.pop('timestamp', now()),
    #     action_string='Hello'
    # )

    newaction=ActivityStreamAction()
    newaction.actor_content_type=ContentType.objects.get_for_model(actor)
    newaction.actor_object_id=actor.pk,
    newaction.verb=unicode(verb),
    newaction.public=bool(kwargs.pop('public', True)),
    newaction.description=kwargs.pop('description', None),
    newaction.timestamp=kwargs.pop('timestamp', now()),
    newaction.action_string='Hello'

    # for opt in ('target', 'action_object'):
    #     obj = kwargs.pop(opt, None)
    #     if not obj is None:
    #         check_actionable_model(obj)
    #         setattr(newaction, '%s_object_id' % opt, obj.pk)
    #         setattr(newaction, '%s_content_type' % opt,
    #                 ContentType.objects.get_for_model(obj))
    # if settings.USE_JSONFIELD and len(kwargs):
    #     newaction.data = kwargs
    newaction.save()


# action.connect(action_handler, dispatch_uid='actstream.models')