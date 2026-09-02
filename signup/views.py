from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages

from .models import UserProfile


# =========================
# SIGNUP
# =========================
def signup(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "customer")

        # Password check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")

        # Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "signup.html")

        # Email check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "signup.html")

        # Role validation
        if role not in ["customer", "admin"]:
            messages.error(request, "Invalid role selected.")
            return render(request, "signup.html")

        # Create Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name
        )

        # Create UserProfile
        UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone
        )

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(request, "signup.html")


# =========================
# LOGIN
# =========================
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages



def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

        except User.DoesNotExist:

            user = None


        if user is not None:

            login(request, user)

            # ADMIN
            if user.is_staff or user.is_superuser:
                return redirect("admin_dashboard")

            # CUSTOMER
            return redirect("dashboard")


        messages.error(
            request,
            "Invalid email or password."
        )


    return render(request, "login.html")
# =========================
# LOGOUT
# =========================
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")