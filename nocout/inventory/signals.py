"""
Module which defines signals.
"""
import os
from PIL import Image

from django.core.files import File
from django.db.models.loading import get_model


def auto_assign_thematic(sender, instance=None, created=False, **kwargs):
    """
    If a new user is created auto assign rssi thematic settings for P2P, PMP and WiMAX technologies.
    """
    UserThematicSettings = get_model('inventory', 'UserThematicSettings', seed_cache=True)
    ThematicSettings = get_model('inventory', 'ThematicSettings', seed_cache=True)

    if not created:
        return

    # Technology P2P
    thematic_setting_p2p = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='P2P',
            name__icontains="RSSI",
    )[:1]

    if len(thematic_setting_p2p)>0:
        UserThematicSettings.objects.create(
                thematic_template=thematic_setting_p2p[0],
                thematic_technology=thematic_setting_p2p[0].threshold_template.live_polling_template.technology,
                user_profile=instance,
        )

    # Technology PMP
    thematic_setting_pmp = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='PMP',
            name__icontains="RSSI",
    )[:1]

    if len(thematic_setting_pmp)>0:
        UserThematicSettings.objects.create(
                thematic_template=thematic_setting_pmp[0],
                thematic_technology=thematic_setting_pmp[0].threshold_template.live_polling_template.technology,
                user_profile=instance,
        )

    # Technology WiMAX
    thematic_setting_wimax = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='WIMAX',
            name__icontains="RSSI",
    )[:1]

    if len(thematic_setting_wimax)>0:
        UserThematicSettings.objects.create(
                thematic_template=thematic_setting_wimax[0],
                thematic_technology=thematic_setting_wimax[0].threshold_template.live_polling_template.technology,
                user_profile=instance,
        )


def resize_icon_size(sender, instance=None, **kwargs):
    """
    Resize the icon as the icon setting is created.
    """
    try:
        image_path = instance.upload_image

        # create PIL Image instance
        image = Image.open(image_path)

        # if not RGB, convert
        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")

        # resize (doing a thumb)
        resize_image = image.resize([32, 32], Image.ANTIALIAS)

        # temporarily save the thumb to the disk
        imagefile = open(os.path.join(unicode(image_path)), 'w')
        resize_image.save(imagefile)

        # get the thumb from the disk
        imagefile = open(os.path.join(unicode(image_path)), 'r')
        content = File(imagefile)

        # remove the temp file from the disk
        os.remove(os.path.join(unicode(image_path)))

        instance.upload_image = content
    except ValueError:
        pass
    except IOError:
        pass


def record_user_password(sender, instance=None, created=False, **kwargs):
    """
    To store the password of user on create/update user profile
    and delete old used password.
    """
    print('+++++++++++++++++signal start')
    UserPasswordRecord = get_model('user_profile', 'UserPasswordRecord', seed_cache=True)
    new_password = instance.password
    current_password = ''
    user_password = UserPasswordRecord.objects.filter(user_id=instance.id)
    print('+++++++++++++++++not user_password.exists')
    if user_password.exists():
        print('+++++++++++++++++user_password.exists')
        current_password = user_password.values_list('password_used', flat=True).\
                            order_by('-password_used_on')[0]
    if new_password != current_password:
        print('+++++++++++++++++new_password!=current_password')
        password_other_than_previous_five = UserPasswordRecord.objects.filter(user_id=instance.id).order_by('-password_used_on')[5:]
        for record in password_other_than_previous_five:
            record.delete()
        UserPasswordRecord.objects.create(user_id=instance.id, password_used=instance.password)
