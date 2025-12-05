import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# from .models import Room
from datetime import datetime, timezone
from pong.tools import create_new_chat_game, does_game_exist, clean_pending_games, lock_for_creation, unlock_for_creation
from .tools import get_banned, is_reciprocal, ban, unban, remove_friend, add_friend, get_friend_of, get_friends, get_general_room_id, save_message, extract_messages, update_message, delete_message
import redis
import logging
from django.apps import apps


Room = apps.get_model('livechat', 'Room')


r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

logger = logging.getLogger(__name__)



class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.rooms = set()
        self.user = self.scope['user']
        self.general = "room_" + str(get_general_room_id()).replace("-", "_")
        self.room_group_name = self.general
        
        
        self.rooms.add(self.room_group_name)
        if self.user.is_authenticated:
            self.user_group_name = f"room_{self.user.username}"
            logger.info(self.user_group_name)
            self.accept()
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            async_to_sync(self.channel_layer.group_add)(
                self.user_group_name,
                self.channel_name
            )
            r.sadd('online_users', self.user.username)
            users_online = list(r.smembers('online_users'))
            self.synchronize(self.general)

            self.update_user_data({})
        else:
            self.close(code=4001)

    def synchronize(self, recipient):
        async_to_sync(self.channel_layer.group_send)(
        recipient,
        {
            "type": "sync",        
        })


    def disconnect(self, close_code):
        if self.user.is_authenticated:
            r.srem('online_users', self.user.username)
            self.synchronize(self.general)
            for room in self.rooms:
                async_to_sync(self.channel_layer.group_discard)(
                    room,
                    self.channel_name
                )

    def receive(self, text_data):
        data = json.loads(text_data) 
        action = data.get('action')
        room_id = data.get('room_id')
        if room_id:
            room_name = "room_" + str(f"{room_id}").replace("-", "_")
            logger.info(f"room_name = {room_name}")
        logger.info(data)

        if action == 'join':       
            self.rooms.add(room_name)
            async_to_sync(self.channel_layer.group_add)(
                room_name,
                self.channel_name            )
            self.send_old_messages(room_name, room_id)

        elif action == 'leave':       
            self.rooms.remove(room_name)
            async_to_sync(self.channel_layer.group_discard)(
                room_name,
                self.channel_name
            )

        elif action == 'message':
            self.room_group_name = room_name
            message = data.get('message')
            sender = data.get('sender')
            msg =  {
            'room_id': room_id,
            'message': message,
            'sender': sender }
            message_id = save_message(msg)
            logger.info(message_id)
            recipients = self.get_other_users(room_id, sender)     
            logger.info(recipients)
            for recipient in recipients:
                logger.info(f"{self.general}_{recipient}")
                async_to_sync(self.channel_layer.group_send)(
                    f"{self.general}_{recipient}",
                    {
                        'type': 'new_message_notification',
                           'room_id':  f"{room_id}",
                           'sender': sender
                    })
            async_to_sync(self.channel_layer.group_send)(
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
            update_message(data)
            async_to_sync(self.channel_layer.group_send)(
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
        elif action == "delete_message":
            message = data.get("message")
            sender = data.get("sender")
            msg_id = data.get("message_id")
            delete_message(msg_id)
            async_to_sync(self.channel_layer.group_send)(
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
                status = add_friend(user, friend)
                message = "success"
                if not status:
                    message = "fail adding friend"
                    status = False
                self.synchronize(self.user_group_name)
                self.notify(self.user_group_name, {"status":status, "message":message})
                if is_reciprocal(user, friend):
                    logger.info(f"1 - status : {status}")     
                    self.synchronize(f"room_{friend}")
                else:
                    logger.info(f"2 - status : friend_request")    
                    self.notify(f"room_{friend}", {"status": "friend_request",
                                     "message" : f"{user} send you a friend request",
                                     "friend": user})

        elif action == "remove_friend":
            user = data.get("sender")
            friend = data.get("user")
            if user and friend:
                status = remove_friend(user, friend)
                message = "success"
                if not status:
                    message = "fail removing friend"
                    status = False
                self.synchronize(self.user_group_name)
                self.synchronize(f"room_{friend}")
                self.notify(self.user_group_name, {"status":status, "message":message})

        elif action == "game_request":
            user = data.get("user")
            friend = data.get("friend")
            async_to_sync(lock_for_creation)(user)
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
            game_uid = async_to_sync(create_new_chat_game)(game)
            game["game_uid"] = game_uid
            self.notify(f"room_{friend}", game)

        elif action == "game_accept":
            user = data.get("user")
            friend = data.get("friend")
            self.notify(f"room_{user}", {"status" : "game_info", "message" : "Your game is ready ! Please join the arena"})
            self.notify(f"room_{friend}", {"status" : "game_info", "message" : "Your game is ready ! Please join the arena"})

            
        elif action == "decline":
            recipient = data["created_by"]
            friend = data["friend"]
            async_to_sync(unlock_for_creation)(recipient)
            async_to_sync(clean_pending_games)()
            game = {}
            game ["status"] = "decline"
            game ["fiend"] = friend
            game ["message"] = f"{friend} can't play right now !"
            self.notify(f"room_{recipient}", game)
            pass


        elif action == "get_users":
            user = data.get("sender")
            self.update_user_data({})


        elif action == "ban":
            user = data.get("sender")
            to_ban = data.get("user")
            status, message = ban(user, to_ban)
            self.synchronize(self.user_group_name)
      
        elif action == "unban":
            user = data.get("sender")
            to_unban = data.get("user")
            status, message = unban(user, to_unban)
            self.synchronize(self.user_group_name)

    def update_user_data(self, content_added):
        users_online = list(r.smembers('online_users'))
        async_to_sync(self.channel_layer.group_send)(
        self.user_group_name,
        {
            "type": "user_list",
            "users": users_online,
            "friends": get_friends(self.user.username),
            "friend_of" : get_friend_of(self.user.username),
            "banned" : get_banned(self.user.username),
            **content_added
        })

    def notify(self, recipient, data):

        async_to_sync(self.channel_layer.group_send)(
        recipient,
        {
            "type" : "notify_user",
            **data,
        })

    # peut etre la mettre em await...    
    def notify_user(self, event):
        status = event.get("status")
        logger.info(f"called with {event}")
        if status:
            if status == "friend_request" or status == "game_request" or status == "decline" or status == "game_info":
                self.send(text_data=json.dumps({**event, "type":status}))
        else:
            self.send(text_data=json.dumps({**event}))


    def chat_message(self, event):
        users_online = list(r.smembers('online_users'))
        message = event['message']
        sender = event['sender']
        room_id = event['room_id']
        message_id = event['message_id']
        now = datetime.now(timezone.utc)
        formatted_date = now.isoformat()

        self.send(text_data=json.dumps({
            'type': 'message',
            'date' : formatted_date,
            'room_id':  f"{room_id}",
            'message': message,
            'sender': sender,
            'id': message_id,
            "users": users_online
        }))

    def new_message_notification(self, event):
        users_online = list(r.smembers('online_users'))
        sender = event['sender']
        room_id = event['room_id']
        type = event['type']

        self.send(text_data=json.dumps({
            'type': type,
            'room_id':  f"{room_id}",
            'sender': sender,
            "users": users_online
        }))    

    def send_online_users(self):
        users_online = list(r.smembers('online_users'))
        async_to_sync(self.channel_layer.group_send)(
            self.channel_name,
            {
                "type": "user_list",
                "users": users_online,
                "friends": get_friends(self.user.username),
                "friend_of" : get_friend_of(self.user.username)
            }
        )

    def send_old_messages(self, room_name, rid):
        users_online = list(r.smembers("online_users"))
        logger.info("received room id")
        logger.info(rid)
        logger.info("name :")
        logger.info(room_name)
        room = Room.objects.filter(room_id=rid).first()
        logger.info(room)
        messages = extract_messages(room)
        async_to_sync(self.channel_layer.group_send)(
                    room_name,
                {
                    'type': 'old_messages',
                    'room_id': f"{rid}",
                    'messages': messages,
                    'users': users_online
                }
        )

    def old_messages(self, event):
        message = event['messages']
        room_id = event['room_id']
        users = event['users']
        self.send(text_data=json.dumps({
            'type': 'archives',
            'room_id': room_id,
            'message': message,
            'users': users
        }))

    def user_list(self, event):
        self.send(text_data=json.dumps({**event}))

    
    def sync(self, event):
        self.send(text_data=json.dumps({**event}))
     
    
    def get_other_users(self, room_id, sender):
        try:
            room = Room.objects.get(room_id=room_id)
            return room.invited.exclude(username=sender)
        except Room.DoesNotExist:
            return []
        
    def update_message(self, event):
        users = list(r.smembers("online_users"))
        self.send(text_data=json.dumps({
            "type": "update_message",
            "sender": event["sender"],
            "message": event["message"],
            "room_id": event["room_id"],
            "message_id": event["message_id"],
            "modified": event["modified"],
            "deleted": event["deleted"],
            "users": users
        }))

    def delete_message(self, event):
        users = list(r.smembers("online_users"))
        self.send(text_data=json.dumps({
            "type": "delete_message",
            "sender": event["sender"],
            "message": event["message"],
            "room_id": event["room_id"],
            "message_id": event["message_id"],
            "modified": event["modified"],
            "deleted": event["deleted"],
             "users": users
        }))

