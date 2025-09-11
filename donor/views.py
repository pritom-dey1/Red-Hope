from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.db import models
from datetime import timedelta
from django.utils import timezone
import random
from django_ratelimit.decorators import ratelimit
from .models import Donor

def donor_list(request):
    donors = Donor.objects.filter(available=True)
    data = [
        {
            "name": donor.user.username,
            "blood_group": donor.blood_group,
            "lat": donor.latitude,
            "lng": donor.longitude,
        }
        for donor in donors
    ]
    return JsonResponse({"donors": data})

from .models import (
    Profile,
    RequestPost,
    DonationRequest,
    Comment,
    Hero,
    ContactMessage,
    ChatMessage,
    Notification,
)

# =========================
# Chat System
# =========================
@login_required
def poll_messages(request, user_id):
    other = get_object_or_404(User, id=user_id)

    last_id = int(request.GET.get("last_id", 0))
    new_msgs = ChatMessage.objects.filter(
        sender=other,
        receiver=request.user,
        id__gt=last_id
    ).order_by("created_at")

    data = [
        {
            "id": m.id,
            "sender_id": m.sender.id,
            "sender_username": m.sender.username,   # 
            "receiver_id": m.receiver.id,
            "receiver_username": m.receiver.username, 
            "message": m.message,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for m in new_msgs
    ]

    new_msgs.update(is_read=True)
    return JsonResponse({"messages": data})


@login_required
@require_POST
def send_message(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    msg = request.POST.get("message")

    if msg and msg.strip():
        m = ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            message=msg.strip()
        )
        return JsonResponse({
            "id": m.id,
            "sender_id": m.sender.id,
            "sender_username": m.sender.username,   
            "receiver_id": m.receiver.id,
            "receiver_username": m.receiver.username,  
            "message": m.message,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return JsonResponse({"error": "Empty message"}, status=400)
@login_required
@require_GET
def chat_users(request):
    users = User.objects.exclude(id=request.user.id)
    data = []
    for u in users:
        profile = getattr(u, "profile", None)
        profile_pic = profile.profile_pic.url if profile and profile.profile_pic else "/static/img/default-avatar.png"
        data.append({
            "id": u.id,
            "username": u.username,
            "profile_pic": profile_pic,  
        })
    return JsonResponse({"users": data})

@login_required
@require_GET
def chat_history(request, user_id):
    other = get_object_or_404(User, id=user_id)
    msgs = ChatMessage.objects.filter(
        models.Q(sender=request.user, receiver=other) |
        models.Q(sender=other, receiver=request.user)
    ).order_by("created_at")

    data = [
        {
            "id": m.id,
            "sender_id": m.sender.id,
            "sender_username": m.sender.username,  
            "receiver_id": m.receiver.id,
            "receiver_username": m.receiver.username,  
            "message": m.message,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for m in msgs
    ]

    ChatMessage.objects.filter(sender=other, receiver=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"messages": data})

def chat_view(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "chat/chat.html", {"users": users})

from .models import (
    Profile,
    RequestPost,
    DonationRequest,
    Comment,
    Hero,
    ContactMessage,
)

# -------------------------
# Temporary storage for verification codes
verification_codes = {}
# -------------------------


# =========================
# Donor Donation Flow
# =========================
@login_required(login_url="login")
def donate_now(request, post_id):
    post = get_object_or_404(RequestPost, id=post_id)

    if request.user.profile.role != "donor":
        messages.error(request, "Only donors can donate.")
        return redirect("pluse")

    last_approved = DonationRequest.objects.filter(
        donor=request.user, status="approved"
    ).order_by("-created_at").first()

    if last_approved:
        next_available_date = last_approved.created_at + timedelta(days=90)
        if timezone.now() < next_available_date:
            remaining_days = (next_available_date - timezone.now()).days
            return render(
                request,
                "donor/cannot_donate.html",
                {"remaining_days": remaining_days}
            )

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        last_date = request.POST.get("last_donation_date")

        donation = DonationRequest.objects.create(
            post=post,
            donor=request.user,
            name=name,
            email=email,
            phone=phone,
            last_donation_date=last_date if last_date else None,
        )

 
        from .models import Notification
        Notification.objects.create(
            user=post.user,  # Post owner = Receiver
            message=f"{request.user.username} sent a donation request for your post ({post.blood_group}, {post.location})",
            link=f"/receiver_dashboard/" 
        )

        return redirect("donation_pending", donation.id)

    return render(request, "donor/donate_form.html", {"post": post})
@login_required(login_url="login")
def donation_pending(request, donation_id):
    donation = get_object_or_404(DonationRequest, id=donation_id, donor=request.user)
    return render(request, "donor/donation_pending.html", {"donation": donation})


# =========================
# Receiver: Manage Donations
# =========================
@login_required(login_url="login")
def manage_donations(request):
    posts = RequestPost.objects.filter(user=request.user)
    donations = DonationRequest.objects.filter(post__in=posts).order_by("-created_at")
    return render(request, "donor/manage_donations.html", {"donations": donations})


@login_required(login_url="login")
def approve_donation(request, donation_id):
    donation = get_object_or_404(DonationRequest, id=donation_id)

    if donation.post.user != request.user:
        messages.error(request, "You are not authorized to approve this donation.")
        return redirect("receiver_dashboard")

    donation.status = "approved"
    donation.save()

    donation.post.post_type = "donated"
    donation.post.save()

    send_mail(
        "Your Donation Request Approved",
        f"Hi {donation.name}, your donation request for {donation.post.name} has been approved. Please proceed to donate.",
        "noreply@bloodpulse.com",
        [donation.email],
        fail_silently=True,
    )

    messages.success(request, "Donation request approved successfully!")
    return redirect("receiver_dashboard")


@login_required(login_url="login")
def reject_donation(request, donation_id):
    donation = get_object_or_404(DonationRequest, id=donation_id)

    if donation.post.user != request.user:
        messages.error(request, "You are not authorized to reject this donation.")
        return redirect("receiver_dashboard")

    donation.status = "rejected"
    donation.save()

    send_mail(
        "Your Donation Request Rejected",
        f"Hi {donation.name}, unfortunately your donation request for {donation.post.name} has been rejected.",
        "noreply@bloodpulse.com",
        [donation.email],
        fail_silently=True,
    )

    messages.warning(request, "Donation request rejected.")
    return redirect("receiver_dashboard")
# =========================
# Comments (AJAX)
# =========================
def get_comments(request, post_id):
    post = get_object_or_404(RequestPost, id=post_id)
    comments = post.comments.all().order_by("-created_at")
    data = [
        {
            "user": c.user.username,
            "text": c.text,
            "created_at": c.created_at.strftime("%b %d, %Y %H:%M"),
        }
        for c in comments
    ]
    return JsonResponse({"comments": data})

@ratelimit(key='ip', rate='3/h', block=False)
@csrf_exempt
def add_comment(request, post_id):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return render(request, "limit_exceeded.html", {"message": "Too many login attempts. Please try again later."})

    
    if request.method == "POST" and request.user.is_authenticated:
        text = request.POST.get("text")
        post = get_object_or_404(RequestPost, id=post_id)
        comment = Comment.objects.create(post=post, user=request.user, text=text)
        return JsonResponse(
            {
                "user": comment.user.username,
                "text": comment.text,
                "created_at": comment.created_at.strftime("%b %d, %Y %H:%M"),
            }
        )
    return JsonResponse({"error": "Invalid request"}, status=400)


# =========================
# Heroes
# =========================
@login_required(login_url="login")
def heroes(request):
    heroes = Hero.objects.all()
    return render(request, "donor/heroes.html", {"heroes": heroes})


@login_required(login_url="login")
def hero_detail(request, pk):
    hero = get_object_or_404(Hero, pk=pk)
    return render(request, "donor/hero_detail.html", {"hero": hero})


# =========================
# Auth & Verification
# =========================
def verify(request, username):
    if request.method == "POST":
        input_code = request.POST.get("code")

        if (
            username in verification_codes
            and str(verification_codes[username]["code"]) == input_code
        ):
            data = verification_codes.pop(username)

            user = User.objects.create_user(
                username=username,
                email=data["email"],
                password=data["password"],
            )
            user.is_active = True
            user.save()

            Profile.objects.create(
                user=user,
                blood_group=data["blood_group"],
                role=data["role"],
            )

            if data["role"] == "donor":
                return redirect("donor_dashboard")
            else:
                return redirect("receiver_dashboard")

        else:
            messages.error(request, "Invalid verification code")
            return redirect("verify", username=username)

    return render(request, "donor/verify.html", {"username": username})

@ratelimit(key='ip', rate='3/h', block=False)
def register(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return render(request, "donor/limit_exceeded.html", {"message": "Too many registration attempts. Please try again later."})
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password1")
        blood_group = request.POST.get("blood_group")
        role = request.POST.get("role")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        code = random.randint(100000, 999999)
        verification_codes[username] = {
            "code": code,
            "email": email,
            "password": password,
            "blood_group": blood_group,
            "role": role,
        }

        send_mail(
            "Your Verification Code",
            f"Hello {username}, your verification code is {code}",
            "your_email@example.com",
            [email],
            fail_silently=False,
        )

        return redirect("verify", username=username)

    return render(request, "donor/registration.html")

@ratelimit(key='ip', rate='3/h', block=False)
def login_view(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return render(request, "donor/limit_exceeded.html", {"message": "Too many registration attempts. Please try again later."})
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if user.profile.role == "donor":
                    return redirect("donor_dashboard")
                else:
                    return redirect("receiver_dashboard")
            else:
                messages.error(request, "Account not active. Please verify your email.")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "donor/login.html")


# =========================
# Donor Dashboard
# =========================
@login_required(login_url="login")
def donor_dashboard(request):
    donations = DonationRequest.objects.filter(donor=request.user).order_by("-created_at")

    total_requests = donations.count()
    total_success = donations.filter(status="approved").count()
    total_rejected = donations.filter(status="rejected").count()
    remaining_for_hero = max(0, 5 - total_success)

    if request.method == "POST" and "profile_pic" in request.FILES:
        profile = request.user.profile
        profile.profile_pic = request.FILES["profile_pic"]
        profile.save()
        messages.success(request, "Profile picture updated successfully!")
        return redirect("donor_dashboard")

    return render(
        request,
        "donor/donor_dashboard.html",
        {
            "donations": donations,
            "total_requests": total_requests,
            "total_success": total_success,
            "total_rejected": total_rejected,
            "remaining_for_hero": remaining_for_hero,
        },
    )


# =========================
# Receiver Dashboard
# =========================
@login_required(login_url="login")
def receiver_dashboard(request):
    posts = RequestPost.objects.filter(user=request.user).order_by("-created_at")
    donations = DonationRequest.objects.filter(post__in=posts).order_by("-created_at")

    if request.method == "POST":
        if "profile_pic" in request.FILES:
            profile = request.user.profile
            profile.profile_pic = request.FILES["profile_pic"]
            profile.save()
            messages.success(request, "Profile picture updated successfully!")
            return redirect("receiver_dashboard")

        name = request.POST.get("name")
        problem = request.POST.get("problem")
        blood_group = request.POST.get("blood_group")
        location = request.POST.get("location")

        if name and problem and blood_group and location:
            post = RequestPost.objects.create(
                user=request.user,
                name=name,
                problem=problem,
                blood_group=blood_group,
                location=location,
                post_type="receiver",
            )

           
            from .models import Profile, Notification

            donors = Profile.objects.filter(role="donor")
            for donor in donors:
                Notification.objects.create(
                    user=donor.user,
                    message=f"{request.user.username} requested {blood_group} blood at {location}",
                    link="/pluse/"  
                )

            messages.success(request, "Blood request posted successfully!")
            return redirect("pluse")

    return render(
        request,
        "donor/receiver_dashboard.html",
        {"posts": posts, "donations": donations},
    )


# =========================
# Posts (pluse feed)
# =========================

@login_required(login_url="login")
def pluse(request):
    posts = RequestPost.objects.all().order_by("-created_at")

    # --- Filtering ---
    blood_group = request.GET.get("blood_group")
    location = request.GET.get("location")
    post_type = request.GET.get("post_type")

    if blood_group and blood_group != "all":
        posts = posts.filter(blood_group=blood_group)

    if location and location != "all":
        posts = posts.filter(location=location)

    if post_type and post_type != "all":
        posts = posts.filter(post_type=post_type)

    # --- Already sent requests by logged-in user ---
    user_requests = []
    if request.user.is_authenticated:
        user_requests = DonationRequest.objects.filter(
            donor=request.user
        ).values_list("post_id", flat=True)

    context = {
        "posts": posts,
        "user_requests": user_requests,
    }
    return render(request, "donor/pluse.html", context)
# =========================
# Static Pages
# =========================
def about(request):
    return render(request, "donor/about.html")


def home(request):
    return render(request, "donor/home.html")


def register_view(request):
    return render(request, "donor/registration.html")


# =========================
# Contact Form (AJAX)
# =========================
@ratelimit(key='ip', rate='5/m', block=False)
def save_contact(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return render(request, "donor/limit_exceeded.html", {"message": "Too many messages sent. Please wait a while."})
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        description = request.POST.get("description")

        if not name or not email or not description:
            return JsonResponse({"success": False, "message": "All fields are required!"})

        ContactMessage.objects.create(name=name, email=email, description=description)
        return JsonResponse({"success": True, "message": "Your message has been sent!"})

    return JsonResponse({"success": False, "message": "Invalid request"})
@login_required(login_url="login")
def get_notifications(request):
    notifications = request.user.notifications.order_by("-created_at")[:20]
    data = [
        {
            "message": n.message,
            "link": n.link,
            "created_at": n.created_at.strftime("%b %d, %Y %H:%M"),
            "is_read": n.is_read,
        }
        for n in notifications
    ]
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({"notifications": data, "count": unread_count})

@login_required(login_url="login")
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def unread_count(request):
    count = request.user.received_messages.filter(is_read=False).count()
    return JsonResponse({"unread_count": count})