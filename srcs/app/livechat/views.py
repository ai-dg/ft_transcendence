from django.shortcuts import render
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.http import JsonResponse
import json
from asgiref.sync import sync_to_async
from server.asyncredis import redis
import logging
from .tools import get_general_room_id, extract_messages
from django.contrib.auth.models import AnonymousUser
from .models import Room


logger = logging.getLogger(__name__)

async def online_users(request):
    users_online = list(await redis.smembers("online_users"))
    return JsonResponse({"users": users_online})


async def get_private_channel(request):

    parsed = json.loads(request.body.decode("utf-8"))
    inviteds = parsed["invited"]

    try:
        user1 = await get_user_model().objects.aget(username=inviteds[0])
        user2 = await get_user_model().objects.aget(username=inviteds[1])
    except ObjectDoesNotExist:
        return JsonResponse({"error": "One or both users not found."}, status=404)    
    room = await sync_to_async(Room.objects.filter(invited=user1).filter(invited=user2).distinct().first)()
    # logger.info(room)
    
    if not room:
        room = await Room.objects.acreate(custom_name=f"{inviteds[0]}-{inviteds[1]}")
        await sync_to_async (room.invited.add)(user1, user2)
        room.asave()
    msg = await extract_messages(room)
    logger.info(f"msg : {msg}")
    return JsonResponse({"room_id": room.room_id, "users": [inviteds[0], inviteds[1]], "messages": msg})
    
async def get_general_room(request):   
    general_room_id = await get_general_room_id()
    return JsonResponse({"room_id": general_room_id})

async def create_channel(request):
    parsed = json.loads(request.body.decode("utf-8"))

    request_type = parsed.get('type')
    if request_type == 'general':
        return await get_general_room(request)
    elif request_type == 'private':
        return await get_private_channel(request)

    return JsonResponse({"error": "invalid room type"}, status=400)


# async def get_messages(request):
#     user = await sync_to_async(lambda: request.user)()
#     if user.is_authenticated:
#         data = None
#         if request.body:
#             data = json.loads(request.body)
#         if not data:
#             return JsonResponse({"status": "error", "message": "invalid request"}, status=400)
#         rid = data["room_id"]
#         try:
#             position = data["position"]
#         except ValueError:
#             logger.error("invalid value for position")
#             return JsonResponse({"status": "error", "message": "invalid request"}, status=400)

#         if request.method == "POST":
#             room = await sync_to_async(lambda: Room.objects.filter(room_id=rid).first())()
#             if not room:
#                 return JsonResponse({"status": "error", "message": "invalid room id"}, status=400)
#             messages = await extract_messages(room)
#             return JsonResponse({
#                 "status": "ok",
#                 "type": "archives",
#                 "room_id": rid,
#                 "message": messages
#             }, status=200)
#         else:
#             return JsonResponse({"status": "error", "message": "invalid method for route"}, status=405)
#     else:
#         return JsonResponse({"status": "error", "message": "User is not authenticated"}, status=401)

    

import json
import logging
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from .models import Room  # Ajustez l'import selon votre structure

logger = logging.getLogger(__name__)

async def get_messages(request):
    # Fonction helper pour obtenir l'utilisateur de manière async
    @sync_to_async
    def get_user_and_check_auth():
        user = request.user
        return user, user.is_authenticated
    
    # Vérification de l'authentification de l'utilisateur
    try:
        user, is_authenticated = await get_user_and_check_auth()
    except Exception as e:
        logger.error(f"Error checking user authentication: {e}")
        return JsonResponse({
            "status": "error", 
            "message": "Authentication error"
        }, status=500)
    
    if not is_authenticated:
        return JsonResponse({
            "status": "error", 
            "message": "User is not authenticated"
        }, status=401)
    
    # Vérification de la méthode HTTP
    if request.method != "POST":
        return JsonResponse({
            "status": "error", 
            "message": "invalid method for route"
        }, status=405)
    
    # Vérification et parsing du body de la requête
    if not request.body:
        return JsonResponse({
            "status": "error", 
            "message": "invalid request"
        }, status=400)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error", 
            "message": "invalid JSON format"
        }, status=400)
    
    # Vérification des données requises
    if not data or "room_id" not in data:
        return JsonResponse({
            "status": "error", 
            "message": "invalid request"
        }, status=400)
    
    rid = data["room_id"]
    
    # Gestion de la position (optionnelle selon votre logique)
    try:
        position = data.get("position", 0)  # Valeur par défaut si non fournie
        if position is not None:
            position = int(position)  # Conversion explicite
    except (ValueError, TypeError):
        logger.error("invalid value for position")
        return JsonResponse({
            "status": "error", 
            "message": "invalid position value"
        }, status=400)
    
    # Fonction helper pour récupérer la room de manière async
    @sync_to_async
    def get_room_by_id(room_id):
        return Room.objects.filter(room_id=room_id).first()
    
    # Récupération de la room
    try:
        room = await get_room_by_id(rid)
    except Exception as e:
        logger.error(f"Database error: {e}")
        return JsonResponse({
            "status": "error", 
            "message": "database error"
        }, status=500)
    
    if not room:
        return JsonResponse({
            "status": "error", 
            "message": "invalid room id"
        }, status=400)
    
    # Extraction des messages
    try:
        messages = await extract_messages(room)
    except Exception as e:
        logger.error(f"Error extracting messages: {e}")
        return JsonResponse({
            "status": "error", 
            "message": "error retrieving messages"
        }, status=500)
    
    return JsonResponse({
        "status": "ok",
        "type": "archives",
        "room_id": rid,
        "message": messages
    }, status=200)