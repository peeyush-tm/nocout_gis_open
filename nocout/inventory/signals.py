import os
from PIL import Image
from django.db.models.signals import pre_save
from django.core.files import File
from django.dispatch import receiver
from inventory.models import IconSettings

@receiver(pre_save, sender=IconSettings)
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
        resize_image.save(imagefile, 'PNG', quality=90)

        # get the thumb from the disk
        imagefile = open(os.path.join(unicode(image_path)), 'r')
        content = File(imagefile)

        # remove the temp file from the disk
        os.remove(os.path.join(unicode(image_path)))

        instance.upload_image = content
    except ValueError:
        pass
