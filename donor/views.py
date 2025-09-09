from django.shortcuts import render
from django.http import JsonResponse
from .models import ContactMessage
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from .models import Profile
import random
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404
from .models import Hero

def heroes(request):
    heroes = Hero.objects.all()
    print("Total heroes in DB:", heroes.count())
    return render(request, 'donor/heroes.html', {'heroes': heroes})

def hero_detail(request, pk):
    hero = get_object_or_404(Hero, pk=pk)
    return render(request, 'donor/hero_detail.html', {'hero': hero})
def verify(request, username):
    if request.method == 'POST':
        input_code = request.POST.get('code')

        if (
            username in verification_codes
            and str(verification_codes[username]["code"]) == input_code
        ):
            data = verification_codes.pop(username)

            # এখনই DB তে user তৈরি করবো
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

            # Redirect role অনুযায়ী
            if data["role"] == "donor":
                return redirect('donor_dashboard')
            else:
                return redirect('receiver_dashboard')

        else:
            messages.error(request, "Invalid verification code")
            return redirect('verify', username=username)

    return render(request, 'donor/verify.html', {'username': username})

def donor_dashboard(request):
    return render(request, 'donor/donor_dashboard.html')
def about(request):
    return render(request , 'donor/about.html')
def receiver_dashboard(request):
    return render(request, 'donor/receiver_dashboard.html')
# Temporary storage for verification codes
verification_codes = {}

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        blood_group = request.POST.get('blood_group')
        role = request.POST.get('role')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        # Generate verification code
        code = random.randint(100000, 999999)
        verification_codes[username] = {
            "code": code,
            "email": email,
            "password": password,
            "blood_group": blood_group,
            "role": role,
        }

        # Send verification email
        send_mail(
            'Your Verification Code',
            f'Hello {username}, your verification code is {code}',
            'your_email@example.com',
            [email],
            fail_silently=False,
        )

        return redirect('verify', username=username)

    return render(request, 'donor/registration.html')

def home(request):
    return render(request, "donor/home.html")


def login_view(request):
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
def register_view(request):
    return render(request, "donor/registration.html")
def save_contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        description = request.POST.get("description")

        if not name or not email or not description:
            return JsonResponse({"success": False, "message": "All fields are required!"})

        ContactMessage.objects.create(
            name=name,
            email=email,
            description=description
        )
        return JsonResponse({"success": True, "message": "Your message has been sent!"})
    return JsonResponse({"success": False, "message": "Invalid request"})
