from .models import Room, Messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import TranscendanceUser
from asgiref.sync import sync_to_async
from server.asyncredis import redis, get_redis

from livechat.models import Ban
import logging
import re



logger = logging.getLogger(__name__)


async def get_general_room_id():
    room, created = await sync_to_async(Room.objects.get_or_create)(system_name="general")
    return room.room_id


# async def extract_messages(room, position=20):
#     users_online = list(await redis.smembers('online_users'))
#     try:
#         r = await Room.objects.aget(room_id=room.room_id)
#         messages = await sync_to_async( lambda: list(Messages.objects.filter(room=r).order_by('-date')[:position].values(
#             'message', 'date', 'author__username', 'read_at', 'id', 'modified', 'deleted'
#         )))()

#         messages_list = []
#         for msg in messages:
#             msg['date'] = msg['date'].isoformat() if msg['date'] else None
#             msg['read_at'] = msg['read_at'].isoformat() if msg['read_at'] else None
#             msg['users'] = users_online
#             messages_list.append(msg)
#         return messages_list
#     except Room.DoesNotExist:
#         logger.error("❌ Error : Room doesn't exist")
#     return []
    

async def extract_messages(room, position=200):
    
    @sync_to_async
    def get_messages_from_db(room_obj, limit):
        try:
            messages = Messages.objects.filter(room=room_obj).order_by('-date')[:limit].values(
                'message', 'date', 'author__username', 'read_at', 'id', 'modified', 'deleted'
            )
            return list(messages)
        except Exception as e:
            logger.error(f"Error getting messages from database: {e}")
            return []
    
    @sync_to_async
    def get_room_from_db(room_id):
        try:
            return Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            logger.error("❌ Error : Room doesn't exist")
            return None
        except Exception as e:
            logger.error(f"Error getting room: {e}")
            return None
    
    try:
        try:
            redis2 = get_redis()
            users_online_set = await redis2.smembers('online_users')
            users_online = list(users_online_set) if users_online_set else []
        except Exception as e:
            logger.error(f"Error getting online users from Redis: {e}")
            users_online = []
        
        r = await get_room_from_db(room.room_id)
        if not r:
            return []
        
        messages = await get_messages_from_db(r, position)
        if not messages:
            return []
        
        messages_list = []
        for msg in messages:
            msg['date'] = msg['date'].isoformat() if msg['date'] else None
            msg['read_at'] = msg['read_at'].isoformat() if msg['read_at'] else None
            msg['users'] = users_online
            messages_list.append(msg)
        
        return messages_list
        
    except Exception as e:
        logger.error(f"Unexpected error in extract_messages: {e}")
        return []


async def save_message(msg):
    try:
        r = await Room.objects.aget(room_id=msg["room_id"])
        sender = await get_user_model().objects.aget(username=msg["sender"])
        msg_instance = await Messages.objects.acreate(message=msg["message"], author = sender, room=r)
        return msg_instance.id
    except Room.DoesNotExist:
        logger.error("❌ Error : Room doesn't exist")
    except get_user_model().DoesNotExist:
        logger.error("❌ Error : User doesn't exist")
    except Exception as e:
        logger.error(f"❌ Unexpected error while saving message: {e}")
    return None

async def delete_message(msg_id):
    try:
        message_instance = await Messages.objects.aget(id=msg_id)
        message_instance.message = "Le message a été supprimé"
        message_instance.modified = False
        message_instance.deleted = True
        message_instance.deleted_at = timezone.now()
        await message_instance.asave()
    except Messages.DoesNotExist:
        logger.error("❌ Error : Message id doesn't exist")

async def update_message(msg):
    try:
        msgid = msg["message_id"]
        if msgid != None:
            number = re.findall(r"\d+", msgid)
            msgid = int(number[0]) if number else None
        logger.info(msgid)
        msg_instance = await Messages.objects.aget(id=msgid)
        msg_instance.message = msg["message"]
        msg_instance.modified = True
        await msg_instance.asave()
        return msg_instance.id
    except Messages.DoesNotExist:
        logger.error("❌ Error : Message id doesn't exist")
    except Exception as e:
        logger.error(f"❌ Unexpected error while saving message: {e}")
    return None

async def ban(user, user_toban):
    try:
        user_field = await get_user_model().objects.aget(username=user)
        try:
            target_user_toban = await get_user_model().objects.aget(username=user_toban)
            try:
                register_ban = await Ban.objects.aget(banned_by=user_field, banned_user=target_user_toban)
                logging.info(f"{user_toban} already banned by {user}")
                return False, "Already banned"
            except Ban.DoesNotExist:
                register_ban = await Ban.objects.acreate(banned_by=user_field, banned_user=target_user_toban)
                logging.info(register_ban)
                logging.info(f"{user} banned {user_toban}")
                return True, "Banned"
        except get_user_model().DoesNotExist:
            logger.error(f"❌ Error: user {user_toban} doesn't exist")
            return False, "failure, user to ban doesn't exist"
    except get_user_model().DoesNotExist:
        logger.error(f"❌ Error: user {user} doesn't exist")
        return False, "❌ failure, user doesn't exist"

async def unban(user, user_to_unban):
    try:
        user_field = await get_user_model().objects.aget(username=user)
        target_to_unban = await get_user_model().objects.aget(username=user_to_unban)
        ban_entry = await sync_to_async( lambda: Ban.objects.filter(banned_by=user_field, banned_user=target_to_unban).first())()
        if (ban_entry):
            logging.info(ban_entry)
            await ban_entry.adelete()
            message = f"{user} unban {user_to_unban}"
            logging.info(message)
            return True, message
        else:
            message = f"{user_to_unban} is not banned"
            logging.info(message)
            return False, message

    except get_user_model().DoesNotExist as e:
        logger.error (f"❌ Error : {e}")
        return False, "failure, user ou banned_user doesn't exist"  
 

async def add_remove_friends(username, friend_username, action):
    if username == friend_username:
        return False
    try:
        user = await get_user_model().objects.aget(username=username)
        user_friend = await get_user_model().objects.aget(username=friend_username)
        if action == "add":
            await sync_to_async(user.friends.add)(user_friend)
        if action == "remove":
            await sync_to_async(user.friends.remove)(user_friend)
            await sync_to_async(user_friend.friends.remove)(user)
        return True
    except get_user_model().DoesNotExist as e:
        logger.info(f"❌ Error : {e} - User ou Friend does not exist !!")
        return False


async def add_friend(user, friend):
    return await add_remove_friends(user, friend, "add")


async def remove_friend(user, friend):
    return await add_remove_friends(user, friend, "remove")


async def _get_friends(username, target="friend"):
    User = get_user_model()

    try:
        user = await User.objects.aget(username=username)
    except User.DoesNotExist :
        return None
    user_friends = None
    if target == "friend_of":
        user_friends = await sync_to_async (list)(user.friend_of.all())
    elif target == "friend":
        user_friends = await sync_to_async (list)(user.friends.all())
    else:
        return None
    return [friend.username for friend in user_friends]


async def get_friend_of(username):
    return await _get_friends(username, target="friend_of")

async def get_friends(username):
    return await _get_friends(username, target="friend")

async def is_reciprocal(user, friend):
    friend_of = await get_friends(friend)
    if user in friend_of:
        return True
    return False
    


@sync_to_async
def get_banned_from_db(user):
    return list(get_user_model().objects.filter(banned_user__banned_by=user))


async def get_banned(username):
    banned_list = []
    try:
        user = await get_user_model().objects.aget(username=username)
        banned_users = await get_banned_from_db(user)
        for banned in banned_users:
            banned_list.append({"username": banned.username})
        
        return banned_list
    except get_user_model().DoesNotExist:
        return banned_list