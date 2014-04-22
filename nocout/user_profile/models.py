from django.db import models
#from auditlog.registry import auditlog
#from audit_log.models.fields import LastUserField
#from audit_log.models.managers import AuditLog
from django.contrib.auth.models import User, UserManager
from user_group.models import UserGroup
from mptt.models import MPTTModel, TreeForeignKey

class UserProfile(MPTTModel, User):
    admin = 'Admin'
    operator = 'Operator'
    viewer = 'Viewer'
    ROLES = (
        (admin, 'Admin'),
        (operator, 'Operator'),
        (viewer, 'Viewer')
    )
    parent = TreeForeignKey('self', null=True, blank=True, related_name='user_children')
    role = models.CharField('Role', max_length=50, choices=ROLES, default=admin )
    user_group = models.ManyToManyField(UserGroup, null=True, blank=True)
    #user_group.help_text = ''
    phone_number = models.CharField('Phone No.', max_length=15, null=True, blank=True)
    company = models.CharField('Company', max_length=100, null=True, blank=True)
    designation = models.CharField('Designation', max_length=100, null=True, blank=True)
    address = models.CharField('Address', max_length=150, null=True, blank=True)
    comment = models.TextField('Comment', null=True, blank=True)
    #audit_log =AuditLog()
  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # Use UserManager to get the create_user method, etc.
    objects = UserManager()
#auditlog.register(UserProfile)      
