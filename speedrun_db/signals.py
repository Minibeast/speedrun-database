import random
from django.db.models import signals
from django.dispatch import receiver

from .models import Run

@receiver(signals.pre_save, sender=Run)
def set_url_id(sender, instance, **kwargs):
    if instance.url_id:
        return
    random_string = ''
    for _ in range(8):
        random_integer = random.randint(97, 97 + 26 - 1)
        flip_bit = random.randint(0, 1)
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer

        random_string += chr(random_integer)
    
    if Run.objects.filter(url_id=random_string).first() is None:
        instance.url_id = random_string
    else:
        set_url_id(sender, instance, kwargs)
        return
