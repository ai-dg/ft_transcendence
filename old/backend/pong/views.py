from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .game import game

# Create your views here.
def pong(request):
    return render(request, 'pong/index.html')

def home(request):
    return render(request, 'pong/index.html')

def start_game(request):
    return JsonResponse({"status": "go"})

def pause_game(request):
    game["status"] = False
    return HttpResponse('{"status":"pause"}')

