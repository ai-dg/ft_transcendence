from django.contrib.auth import get_user_model, logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
# from .game import game
from .models import *
from django.http import JsonResponse
import redis, logging
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Create your views here.
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
logger = logging.getLogger(__name__)

def get_user(request):
    user_id = request.user.id
    username = request.user.username
    
    if user_id and username:
        return JsonResponse({'username': username})
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

def get_user_sessions(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        user_requested = request.GET.get('user')

        if not user_requested or len(user_requested) == 0:
            return JsonResponse({'error': 'User not provided'}, status=400)
        
        try:
            user = get_user_model().objects.get(username=user_requested)
        except get_user_model().DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)

        sessions = Session.objects.filter(
            Q(player1=user) | Q(player2=user)
        ).select_related('player1', 'player2', 'winner_id') \
         .order_by('-ended_at')

        # custom JSON structure
        session_data = []
        for session in sessions:
            session_data.append({
                'player1': session.player1.username if session.player1 else None,
                'player2': session.player2.username if session.player2 else None,
                'is_multiplayer': session.is_multiplayer,
                'player1_score': session.player1_score,
                'player2_score': session.player2_score,
                'ended_at': session.ended_at,
                'winner': session.winner_id.username if session.winner_id else None,
            })
        
        return JsonResponse(session_data, safe=False)
    
def get_user_stats(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        user_requested = request.GET.get('user')

        if not user_requested or len(user_requested) == 0:
            return JsonResponse({'error': 'User not provided'}, status=400)
        
        try:
            user = get_user_model().objects.get(username=user_requested)
        except get_user_model().DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        
        sessions = Session.objects.filter(Q(player1=user) | Q(player2=user))

        total_games_played = 0
        total_games_won = 0
        total_points_scored = 0
        total_points_conceded = 0
        for session in sessions:
            total_games_played += 1
            if session.player1 == user:
                total_points_scored += session.player1_score
                total_points_conceded += session.player2_score
            else:
                total_points_scored += session.player2_score
                total_points_conceded += session.player1_score
            total_games_won += session.winner_id == user
        
        tournaments = Tournament.objects.filter(
            Q(session__player1=user) | Q(session__player2=user)
        ).distinct()
        
        total_tournaments_played = 0
        total_tournaments_won = 0
        
        for tournament in tournaments:
            total_tournaments_played += 1
            total_tournaments_won += tournament.winner_id == user

        return JsonResponse({
            'total_games_played': total_games_played,
            'total_games_won': total_games_won,
            'total_points_scored': total_points_scored,
            'total_points_conceded': total_points_conceded,
            'total_tournaments_played': total_tournaments_played,
            'total_tournaments_won': total_tournaments_won
        })

    

def pong(request):
    if not request.user.is_authenticated:
        return render(request, 'accounts/login.html')
    context = { 'room_name' : 'General Chat', 'username': request.user.username, 'tournament_pseudo': request.user.tournament_pseudo}
    return render(request, "pong/index.html", context)

def logout_view(request):
    r.srem('online_users', request.session["username"] )
    logout(request)
    request.session.flush() 
    return redirect("pong")
