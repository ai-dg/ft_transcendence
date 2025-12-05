import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import  sync_to_async
from channels.layers import get_channel_layer
# from .models import Room
from datetime import datetime, timezone
from pong.tools import create_new_chat_game, does_game_exist, clean_pending_games, lock_for_creation, unlock_for_creation
from .tools import get_banned, is_reciprocal, ban, unban, remove_friend, add_friend, get_friend_of, get_friends, get_general_room_id, save_message, extract_messages, update_message, delete_message
from server.asyncredis import redis
import logging
from django.apps import apps


Room = apps.get_model('livechat', 'Room')


# r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.rooms = set()
        self.user = self.scope['user']
        self.general = "room_" + str(await get_general_room_id()).replace("-", "_")
        self.room_group_name = self.general
        
        
        self.rooms.add(self.room_group_name)
        if self.user.is_authenticated:
            self.user_group_name = f"room_{self.user.username}"
            await self.accept()
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await redis.sadd('online_users', self.user.username)
            users_online = list(await redis.smembers('online_users'))
            await self.synchronize(self.general)

            await self.update_user_data({})
        else:
            await self.close(code=4001)

    async def synchronize(self, recipient):
        await self.channel_layer.group_send(
        recipient,
        {
            "type": "sync",        
        })


    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await redis.srem('online_users', self.user.username)
            await self.synchronize(self.general)
            for room in self.rooms:
                await self.channel_layer.group_discard(
                    room,
                    self.channel_name
                )
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data) 
        action = data.get('action')
        room_id = data.get('room_id')
        if room_id:
            room_name = "room_" + str(f"{room_id}").replace("-", "_")

        if action == 'join':       
            self.rooms.add(room_name)
            await self.channel_layer.group_add(
                room_name,
                self.channel_name            )
            await self.send_old_messages(room_name, room_id)

        elif action == 'leave':       
            self.rooms.remove(room_name)
            await redis.srem('online_users', self.user.username)
            await self.channel_layer.group_discard(
                room_name,
                self.channel_name
            )

        elif action == 'update':
            await self.send_old_messages(room_name, room_id)

        elif action == 'message':
            self.room_group_name = room_name
            message = data.get('message')
            sender = data.get('sender')
            msg =  {
            'room_id': room_id,
            'message': message,
            'sender': sender }
            message_id = await save_message(msg)
            recipients = await self.get_other_users(room_id, sender)
            for recipient in recipients:
                logger.info(f"MESSAGE RECIPIENTS : {recipient}")
                await self.channel_layer.group_send(
                    f"room_{recipient}",
                    {
                        'type': 'new_message_notification',
                           'room_id':  f"{room_id}",
                           'sender': sender
                    })
            await self.channel_layer.group_send(
                room_name,
            {
                'type': 'chat_message',
                'room_id': f"{room_id}",
                'message': message,
                'sender': sender,
                'message_id': message_id
            })

        elif action == "update_message" :
            #modify message in bdd
            message = data.get("message")
            sender = data.get("sender")
            await update_message(data)
            await self.channel_layer.group_send(
                room_name,
            {
                'type': 'update_message',
                'room_id': f"{room_id}",
                'message': message,
                'sender': sender,
                'message_id': data.get("message_id"),
                'modified': "True",
                'deleted': "False"
            })

        elif action == "account_update":
            user = data.get("user")
            await self.notify(self.room_group_name, {"username" : user, "status" : "new_avatar"})


        elif action == "delete_message":
            message = data.get("message")
            sender = data.get("sender")
            msg_id = data.get("message_id")
            await delete_message(msg_id)
            await self.channel_layer.group_send(
                room_name,
            {
                'type': 'delete_message',
                'room_id': f"{room_id}",
                'message': message,
                'sender': sender,
                'message_id': data.get("message_id"),
                'modified': "False",
                'deleted': "True"
            })

        elif action == "add_friend":
            user = data.get("sender")
            friend = data.get("user")
            if user and friend:
                status = await add_friend(user, friend)
                message = "success"
                if not status:
                    message = "fail adding friend"
                    status = False
                await self.synchronize(self.user_group_name)
                await self.notify(self.user_group_name, {"status":status, "message":message})
                if await is_reciprocal(user, friend):
                    await self.synchronize(f"room_{friend}")
                else: 
                    await self.notify(f"room_{friend}", {"status": "friend_request",
                                     "message" : f"{user} send you a friend request",
                                     "friend": user})

        elif action == "remove_friend":
            user = data.get("sender")
            friend = data.get("user")
            if user and friend:
                status = await remove_friend(user, friend)
                message = "success"
                if not status:
                    message = "fail removing friend"
                    status = False
                await self.synchronize(self.user_group_name)
                await self.synchronize(f"room_{friend}")
                await self.notify(self.user_group_name, {"status":status, "message":message})

        elif action == "game_request":
            user = data.get("user")
            friend = data.get("friend")
            await lock_for_creation(user)
            game = {}
            game["player1"] = user
            game["players"] = 1
            game["created_by"] = user
            game["from_tournament"] = False
            game ["tournament_uid"] = None
            game["game_param"] = data["game_param"]
            game["status"] = "game_request"
            game["message"] = f"{user} send you a game request"
            game["friend"] = user
            game_uid = await create_new_chat_game(game)
            game["game_uid"] = game_uid
            await self.notify(f"room_{friend}", game)

        elif action == "game_accept":
            user = data.get("user")
            friend = data.get("friend")
            now = datetime.now(timezone.utc).isoformat()
            await self.notify(f"room_{user}", {"status" : "game_info", "message" : "Your game is ready ! Please join the arena", "date" : now})
            await self.notify(f"room_{friend}", {"status" : "game_info", "message" : "Your game is ready ! Please join the arena", "date": now})

            
        elif action == "decline":
            recipient = data["created_by"]
            friend = data["friend"]
            await unlock_for_creation(recipient)
            await clean_pending_games()
            game = {}
            game ["status"] = "decline"
            game ["fiend"] = friend
            game ["message"] = f"{friend} can't play right now !"
            await self.notify(f"room_{recipient}", game)


        elif action == "get_users":
            user = data.get("sender")
            await self.update_user_data({})


        elif action == "ban":
            user = data.get("sender")
            to_ban = data.get("user")
            status, message = await ban(user, to_ban)
            await self.synchronize(self.user_group_name)
      
        elif action == "unban":
            user = data.get("sender")
            to_unban = data.get("user")
            status, message = await unban(user, to_unban)
            await self.synchronize(self.user_group_name)

    async def update_user_data(self, content_added):
        users_online = list(await redis.smembers('online_users'))
        friends = await get_friends(self.user.username)
        friend_of = await get_friend_of(self.user.username)
        banned = await get_banned(self.user.username)
        await self.channel_layer.group_send(
        self.user_group_name,
        {
            "type": "user_list",
            "users": users_online,
            "friends": friends,
            "friend_of" : friend_of,
            "banned" : banned,
            **content_added
        })

    async def notify(self, recipient, data):

        await self.channel_layer.group_send(
        recipient,
        {
            "type" : "notify_user",
            **data,
        })

    # peut etre la mettre em await...    
    async def notify_user(self, event):
        status = event.get("status")
        logger.info(f"STATUS IN NOTIFY {status}")
        if status:
            logger.info("TRUE IN")
            if status == "friend_request" or status == "game_request" or status == "decline" or status == "game_info" or status == "new_avatar":
                await self.send(text_data=json.dumps({**event, "type":status}))
        else:
            await self.send(text_data=json.dumps({**event}))


    async def chat_message(self, event):
        users_online = list(await redis.smembers('online_users'))
        message = event['message']
        sender = event['sender']
        room_id = event['room_id']
        message_id = event['message_id']
        now = datetime.now(timezone.utc)
        formatted_date = now.isoformat()

        await self.send(text_data=json.dumps({
            'type': 'message',
            'date' : formatted_date,
            'room_id':  f"{room_id}",
            'message': message,
            'sender': sender,
            'id': message_id,
            "users": users_online
        }))

    async def new_message_notification(self, event):
        users_online = list(await redis.smembers('online_users'))
        sender = event['sender']
        room_id = event['room_id']
        type = event['type']

        await self.send(text_data=json.dumps({
            'type': type,
            'room_id':  f"{room_id}",
            'sender': sender,
            "users": users_online
        }))    

    async def send_online_users(self):
        users_online = list(await redis.smembers('online_users'))
        friends = await get_friends(self.user.username)
        friends_of = await get_friend_of(self.user.username)
        await self.channel_layer.group_send(
            self.channel_name,
            {
                "type": "user_list",
                "users": users_online,
                "friends": friends ,
                "friend_of" : friends_of
            }
        )

    async def send_old_messages(self, room_name, rid):
        users_online = list(await redis.smembers("online_users"))
        room = await sync_to_async( lambda: Room.objects.filter(room_id=rid).first())()
        messages = await extract_messages(room)
        await self.channel_layer.group_send(
                    room_name,
                {
                    'type': 'old_messages',
                    'room_id': f"{rid}",
                    'messages': messages,
                    'users': users_online
                }
        )

    async def old_messages(self, event):
        message = event['messages']
        room_id = event['room_id']
        users = event['users']
        await self.send(text_data=json.dumps({
            'type': 'archives',
            'room_id': room_id,
            'message': message,
            'users': users
        }))

    async def user_list(self, event):
        await self.send(text_data=json.dumps({**event}))

    
    async def sync(self, event):
        await self.send(text_data=json.dumps({**event}))
     
    
    async def get_other_users(self, room_id, sender):
        try:
            room = await Room.objects.aget(room_id=room_id)
            other_users = await sync_to_async(lambda: list(room.invited.exclude(username=sender)))()
            
            return other_users
        except Room.DoesNotExist:
            return []
        
    async def update_message(self, event):
        users = list(await redis.smembers("online_users"))
        await self.send(text_data=json.dumps({
            "type": "update_message",
            "sender": event["sender"],
            "message": event["message"],
            "room_id": event["room_id"],
            "message_id": event["message_id"],
            "modified": event["modified"],
            "deleted": event["deleted"],
            "users": users
        }))

    async def delete_message(self, event):
        users = list(await redis.smembers("online_users"))
        await self.send(text_data=json.dumps({
            "type": "delete_message",
            "sender": event["sender"],
            "message": event["message"],
            "room_id": event["room_id"],
            "message_id": event["message_id"],
            "modified": event["modified"],
            "deleted": event["deleted"],
             "users": users
        }))

