"""
Module which defines signals.
"""
import os
from PIL import Image

from django.core.files import File
from django.db.models.loading import get_model

# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


def update_site_on_bs_bhport_change(sender, instance=None, created=False, **kwargs):
    """
    Signal to modify site 'id_device_change' field, if 'bh_port_name' field change.
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    from inventory.models import BaseStation

    # Old Instance.
    old_instance = None
    try:
        old_instance = BaseStation.objects.get(id=instance.id)
    except Exception as e:
        pass

    if old_instance:
        # List containing old values of fields.
        old_values = [old_instance.bh_port_name,
                      old_instance.bh_capacity]
        old_values = [x for x in old_values if x is not None]

        # List containing new values of fields.
        new_values = [instance.bh_port_name,
                      instance.bh_capacity]
        new_values = [x for x in new_values if x is not None]

        if (len(new_values) != len(old_values)) or (list(set(old_values) - set(new_values))):
            old_backhaul = old_instance.backhaul
            if old_backhaul and old_backhaul.bh_configured_on and old_backhaul.bh_configured_on.site_instance:
                site = old_instance.backhaul.bh_configured_on.site_instance
                # Modify site bit.
                site.is_device_change = 1
                site.save()


@nocout_utils.disable_for_loaddata
def auto_assign_thematic(sender, instance=None, created=False, **kwargs):
    """
    If a new user is created auto assign rssi thematic settings for P2P, PMP and WiMAX technologies.
    """
    UserThematicSettings = get_model('inventory', 'UserThematicSettings')
    ThematicSettings = get_model('inventory', 'ThematicSettings')

    if not created:
        return

    # Technology P2P
    thematic_setting_p2p = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='P2P',
            name__icontains="RSSI",
    )

    if len(thematic_setting_p2p)>0:
        added_type = list()
        for obj in thematic_setting_p2p:
            if obj.threshold_template.live_polling_template.device_type.id not in added_type:
                added_type.append(obj.threshold_template.live_polling_template.device_type.id)
                UserThematicSettings.objects.create(
                        thematic_template=obj,
                        thematic_technology=obj.threshold_template.live_polling_template.technology,
                        thematic_type=obj.threshold_template.live_polling_template.device_type,
                        user_profile=instance,
                )


    # Technology PMP
    thematic_setting_pmp = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='PMP',
            name__icontains="RSSI",
    )

    if len(thematic_setting_pmp)>0:
        added_type = list()
        for obj in thematic_setting_pmp:
            if obj.threshold_template.live_polling_template.device_type.id not in added_type:
                added_type.append(obj.threshold_template.live_polling_template.device_type.id)
                UserThematicSettings.objects.create(
                        thematic_template=obj,
                        thematic_technology=obj.threshold_template.live_polling_template.technology,
                        thematic_type=obj.threshold_template.live_polling_template.device_type,
                        user_profile=instance,
                )


    # Technology WiMAX
    thematic_setting_wimax = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='WIMAX',
            name__icontains="RSSI",
    )

    if len(thematic_setting_wimax) > 0:
        added_type = list()
        for obj in thematic_setting_wimax:
            if obj.threshold_template.live_polling_template.device_type.id not in added_type:
                added_type.append(obj.threshold_template.live_polling_template.device_type.id)
                UserThematicSettings.objects.create(
                        thematic_template=obj,
                        thematic_technology=obj.threshold_template.live_polling_template.technology,
                        thematic_type=obj.threshold_template.live_polling_template.device_type,
                        user_profile=instance,
                )


@nocout_utils.disable_for_loaddata
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


@nocout_utils.disable_for_loaddata
def delete_antenna_of_sector(sender, instance=None, **kwargs):
    """
    Deletes the antenna of a sector if sector is deleted.
    """
    if instance.antenna:
        instance.antenna.delete()


@nocout_utils.disable_for_loaddata
def delete_antenna_of_substation(sender, instance=None, **kwargs):
    """
    Deletes the antenna of a sub-station if sub-station is deleted.
    """
    if instance.antenna:
        instance.antenna.delete()


@nocout_utils.disable_for_loaddata
def delete_customer_of_circuit(sender, instance=None, **kwargs):
    """
    Deletes the customer of a circuit if circuit is deleted.
    """
    if instance.customer:
        instance.customer.delete()
