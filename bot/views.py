# Create your views here.
import json
import os

from django.contrib.auth import authenticate
from django.contrib.auth import login as user_login, logout as user_logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from .models import Region

load_dotenv()


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


def map(request):
    return render(request, 'map.html', {
        'key': os.getenv('GOOGLE_MAPS_API_KEY')
    })


def track(request):
    region = Region.objects.last()
    return render(request, 'track.html', {
        'region': region,
        'key': os.getenv('GOOGLE_MAPS_API_KEY')
    })


def save_region(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', 'Unnamed Region')
            points = data.get('points')

            if not points or not isinstance(points, list):
                return JsonResponse({'error': 'Invalid points data. Must be a list of lat/lng pairs.'}, status=400)

            # Save the region with points as JSON
            region = Region.objects.create(name=name, points=points)

            return JsonResponse({'message': 'Region saved successfully.'}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Error saving region: {str(e)}'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def get_region_points(request):
    # Get the last region object
    region = Region.objects.last()

    if region is None:
        # Handle the case where no region exists
        return JsonResponse({'error': 'No region found'}, status=404)

    # Serialize the region object
    region_data = {
        'points': region.points,  # Replace with actual field names
    }

    return JsonResponse(region_data)
