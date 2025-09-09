from django.db import models
from django.contrib.auth.models import User


# =====================
# Post Model
# =====================
class RequestPost(models.Model):
    BANGLADESH_DISTRICTS = [
        ('Dhaka', 'Dhaka'), ('Chattogram', 'Chattogram'),
        ('Rajshahi', 'Rajshahi'), ('Khulna', 'Khulna'),
        ('Barishal', 'Barishal'), ('Sylhet', 'Sylhet'),
        ('Rangpur', 'Rangpur'), ('Mymensingh', 'Mymensingh'),
    ]

    POST_TYPE_CHOICES = [
        ('receiver', 'Receiver'),
        ('donor', 'Donor'),
        ('donated', 'Donated'),   # extra state for approved donation
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    problem = models.TextField()
    blood_group = models.CharField(max_length=5)
    location = models.CharField(max_length=50, choices=BANGLADESH_DISTRICTS)
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='receiver')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.blood_group} ({self.post_type})"


# =====================
# Donation Request Model
# =====================
class DonationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    post = models.ForeignKey(RequestPost, on_delete=models.CASCADE, related_name="donations")
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donations")
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    last_donation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donation by {self.name} for {self.post}"


# =====================
# Comment Model
# =====================
class Comment(models.Model):
    post = models.ForeignKey(RequestPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"


# =====================
# Profile Model
# =====================
class Profile(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    ROLE_CHOICES = [
        ('donor', 'Donor'),
        ('receiver', 'Receiver')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    profile_pic = models.ImageField(upload_to="profile_pics/", default="default.jpg")

    def __str__(self):
        return self.user.username


# =====================
# Contact Model
# =====================
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =====================
# Hero Model (for homepage section)
# =====================
class Hero(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="heroes/")

    def __str__(self):
        return self.name
