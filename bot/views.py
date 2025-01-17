# Create your views here.
from django.contrib.auth import authenticate
from django.contrib.auth import login as user_login, logout as user_logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse


def index(request):
    return render(request, 'index.html') if request.user.is_authenticated else redirect('login')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            user_login(request, user)
            return redirect('index')
        else:
            return render(request, "auth/login.html", {
                "message": "Invalid username and/or password."
            })

    return render(request, 'auth/login.html') if request.user.is_anonymous else redirect('index')


def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirm_password"]
        role = request.POST.get("role")

        if password != confirmation:
            return render(request, "auth/register.html", {
                "message": "Passwords must match."
            })

        if not role or role not in ["manager", "employee"]:
            return render(request, "auth/register.html", {
                "message": "Please select a valid role."
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
            user.save()

            # Save the role in the profile
            user.profile.role = role
            user.profile.save()
        except IntegrityError:
            return render(request, "auth/register.html", {
                "message": "Username already taken."
            })

        user_login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auth/register.html")


def logout(request):
    user_logout(request)
    return redirect('index')


def dashboard(request):
    # Get all users with profile.role = 'employee'
    employees = User.objects.filter(profile__role='employee')
    return render(request, 'dashboard.html', {
        'employees': employees
    })


def reports(request):
    return render(request, 'reports.html')


def metrics(request, username):
    # Mock data for demonstration
    profile_user = User.objects.get(username=username)
    context = {
        'profile_user': profile_user,
        'pulse_detected': True,  # Example: Pulse detected
        'temperature': 20,  # Example: Body temperature in °C
        'gas_level': 'Safe',  # Options: 'Safe', 'Caution', 'Danger'
        'overhead_status': 'Caution',  # Options: 'Safe', 'Caution', 'Danger'
        'torch_status': True,  # Example: Torch is ON
        'online_status': True,  # Example: User is online
    }
    return render(request, 'metrics.html', context)
