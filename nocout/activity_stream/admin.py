from actstream.models import Action, Follow
from django.utils.translation import ugettext as _
from django.contrib import admin



# class ActivityStreamAction(Action):
#
#     class Meta:
#         proxy=True
#
#     def __unicode__(self):
#         ctx = {
#             'actor': self.actor,
#             'verb': self.verb,
#             'action_object': self.action_object,
#             'action_object_class':self.action_object.__class__,
#             'target': self.target,
#             'target_class':self.target.__class__,
#             'timesince': self.timesince()
#         }
#
#         if self.target:
#             ctx.update(dict(target_class=self.target.__class__))
#             if self.action_object:
#                 ctx.update(dict(action_object_class=self.action_object.__class__))
#                 return _('%(actor)s %(verb)s %(action_object)s %(action_object_class) on %(target)s %(target_class)s %(timesince)s ago') % ctx
#             return _('%(actor)s %(verb)s %(target)s %(target_class)s %(timesince)s ago') % ctx
#         if self.action_object:
#             ctx.update(dict(action_object_class=self.action_object.__class__))
#             return _('%(actor)s %(verb)s %(action_object)s %(action_object_class)s %(timesince)s ago') % ctx
#         return _('%(actor)s %(verb)s %(timesince)s ago') % ctx

def myunicode(self):
    ctx = {
        'verb': self.verb,
        'action_object': self.action_object,
        'target': self.target,
        'timesince': self.timesince()
    }

    if self.target:
        ctx.update(dict(target_class=self.target.__class__.__name__))
        if self.action_object:
            ctx.update(dict(action_object_class=self.action_object.__class__.__name__))
            return _('%(verb)s %(action_object)s (%(action_object_class)s) on %(target)s (%(target_class)s) %(timesince)s ago') % ctx
        return _(' %(verb)s %(target)s (%(target_class)s) %(timesince)s ago') % ctx
    if self.action_object:
        ctx.update(dict(action_object_class=self.action_object.__class__.__name__))
        return _('%(verb)s %(action_object)s (%(action_object_class)s) %(timesince)s ago') % ctx
    return _('%(verb)s %(timesince)s ago') % ctx

def mystr(self):
    ctx = {
        'actor': self.actor,
        'verb': self.verb,
        'action_object': self.action_object,
        'target': self.target,
        'timesince': self.timesince()
    }

    if self.target:
        ctx.update(dict(target_class=self.target.__class__.__name__))
        if self.action_object:
            ctx.update(dict(action_object_class=self.action_object.__class__.__name__))
            return _('%(actor)s %(verb)s %(action_object)s (%(action_object_class)s) on %(target)s (%(target_class)s) %(timesince)s ago') % ctx
        return _('%(actor)s %(verb)s %(target)s (%(target_class)s) %(timesince)s ago') % ctx
    if self.action_object:
        ctx.update(dict(action_object_class=self.action_object.__class__.__name__))
        return _('%(actor)s %(verb)s %(action_object)s (%(action_object_class)s) %(timesince)s ago') % ctx
    return _('%(actor)s %(verb)s %(timesince)s ago') % ctx


Action.__unicode__ = myunicode
Action.__str__ = mystr

admin.site.unregister(Action)
admin.site.register(Action)
admin.site.unregister(Follow)







