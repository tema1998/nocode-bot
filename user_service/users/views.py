from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views import View

from .forms import LoginForm, RegisterForm


class RegisterView(View):
    """
    View for user registration.
    Handles both GET and POST requests for the registration form.
    """

    def get(self, request):
        """
        Handles GET requests.
        Renders the registration form.
        """
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

    def post(self, request):
        """
        Handles POST requests.
        Processes the registration form data.
        If the form is valid, creates a new user, logs them in, and redirects to the home page.
        If the form is invalid, re-renders the form with error messages.
        """
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user
            login(request, user)  # Log the user in
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("home")
        return render(request, "users/register.html", {"form": form})


class LoginView(View):
    """
    View for user login.
    Handles both GET and POST requests for the login form.
    """

    def get(self, request):
        """
        Handles GET requests.
        Renders the login form.
        """
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})

    def post(self, request):
        """
        Handles POST requests.
        Processes the login form data.
        If the form is valid and the user is authenticated, logs them in and redirects to the home page.
        If the form is invalid or authentication fails, re-renders the form with error messages.
        """
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get(
                "username"
            )  # Get username from the form
            password = form.cleaned_data.get(
                "password"
            )  # Get password from the form
            user = authenticate(
                username=username, password=password
            )  # Authenticate the user
            if user is not None:
                login(request, user)  # Log the user in
                messages.success(request, f"Добро пожаловать, {username}!")
                return redirect("home")
        return render(request, "users/login.html", {"form": form})


class LogoutView(View):
    """
    View for user logout.
    Handles GET requests to log the user out.
    """

    def get(self, request):
        """
        Handles GET requests.
        Logs the user out and redirects to the registration page.
        """
        logout(request)  # Log the user out
        messages.success(request, "Вы вышли из системы.")
        return redirect("index")
