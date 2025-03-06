from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
# from .game import game
from .models import *

# Create your views here.

def pong(request):
    logged = "user_id" in request.session

    if request.method == "POST":
        if "username_register" in request.POST:
            username = request.POST.get("username_register", "").strip()
            password = request.POST.get("password_register", "").strip()

            if username and password:
                if Account.objects.filter(username=username).exists():
                    return render(request, "pong/index.html", {
                        "message": "Username already taken.",
                        "logged": logged
                    })
                else:
                    account = Account(username=username)
                    account.set_password(password)
                    account.save()
                    return render(request, "pong/index.html", {
                        "message": "Account created successfully.",
                        "logged": logged
                    })
            else:
                return render(request, "pong/index.html", {
                    "message": "Username and password cannot be empty.",
                    "logged": logged
                })

        if "username_login" in request.POST:
            username = request.POST["username_login"]
            password = request.POST["password_login"]

            try:
                user = Account.objects.get(username=username)
                if user.check_password(password):
                    request.session["user_id"] = user.id
                    request.session["username"] = user.username
                    return render(request, "pong/index.html", {
                        "logged": True
                        })
                else:
                    return render(request, "pong/index.html", {
                        "message": "Invalid credentials.",
                        "logged": logged
                    })
            except Account.DoesNotExist:
                return render(request, "pong/index.html", {
                    "message": "Invalid credentials.",
                    "logged": logged
                })

    return render(request, "pong/index.html", {"logged": logged})

def logout_view(request):
    logout(request)
    request.session.flush() 
    return redirect("pong")
    # return render(request, 'pong/index.html', {
    #     "logged": False,
    # })

def home(request):
    return render(request, 'pong/index.html')

def start_game(request):
    return JsonResponse({"status": "start"})

def pause_game(request):
    # game["status"] = False
    return HttpResponse('{"status":"stop"}')