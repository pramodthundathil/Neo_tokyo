from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, load_backend, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def signin(request):
    if request.method == "POST":
        username = request.POST.get("uname")
        password = request.POST.get("pswd")
        user = authenticate(request, email=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("admin_board")
        else:
            messages.error(request, "Invalid username or password.")
            redirect("signin")
    return render(request, "login.html")