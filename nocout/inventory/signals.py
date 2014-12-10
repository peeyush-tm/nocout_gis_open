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


def delete_antenna_of_sector(sender, instance=None, **kwargs):
    """
    Deletes the antenna of a sector if sector is deleted.
    """
    instance.antenna.delete()


def delete_antenna_of_substation(sender, instance=None, **kwargs):
    """
    Deletes the antenna of a sub-station if sub-station is deleted.
    """
    instance.antenna.delete()

def delete_customer_of_circuit(sender, instance=None, **kwargs):
    """
    Deletes the customer of a circuit if circuit is deleted.
    """
    instance.customer.delete()
