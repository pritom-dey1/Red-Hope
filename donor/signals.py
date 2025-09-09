from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DonationRequest, RequestPost

@receiver(post_save, sender=DonationRequest)
def update_post_on_approval(sender, instance, **kwargs):

    if instance.status == "approved":
        post = instance.post
        if post.post_type != "donated":
            post.post_type = "donated"
            post.save()
