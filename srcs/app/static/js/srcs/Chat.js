import { get_user } from "./User.js";
import { getUrl } from "./Urls.js";
import { chat_socket } from "./RegisterSockets.js";
import { formatDate } from "./Date.js";
import { initEmojis } from "./Emojis.js";
import { User } from "./User.js";
import { reloadAvatar, getAvatarFromUser } from "./Avatars.js";
import { USER_ACTION, userHandler } from "./handlers.js";
import { resetElement } from "./dom_utils.js";
import { DELETE } from "./const.js";
import { getCSRFToken } from "./Security.js";
import { DEFAULT_GAME_PARAMS } from "./Game.js";
import { getElements } from "./uitools.js";
const custom = new CustomEvent('userready');
export const rooms_ids = new Set();
export async function getRoomMessages(room_id, position = -1) {
    const token = getCSRFToken();
    try {
        const response = await fetch(getUrl("chat/getmessages"), {
            method: "POST",
            headers: {
                "content-type": "application/json",
                "X-CSRFToken": token
            },
            body: JSON.stringify({
                position: position,
                room_id: room_id
            })
        });
        const data = await response.json();
        return data;
    }
    catch (err) {
        console.error(err);
        return null;
    }
}
export function update_message(data, deleted = false) {
    let msg = document.querySelector(`[msg-id="${data.message_id}"]`);
    if (msg) {
        if (deleted)
            msg.innerHTML = `<i class="modified_message">message supprimé</i>`;
        else
            msg.innerHTML = `${data.message} <i class="modified_message">modifié</i>`;
    }
}
export async function updateRooms(position = -1) {
    for (const room_id of rooms_ids) {
        const room_element = document.querySelector(`[room_id="${room_id}"]`);
        resetChatRoom(room_id);
        const data = await getRoomMessages(room_id, position);
        if (data) {
            displayOldMessages(room_id, data.message);
        }
        else {
            console.error("Erreur lors de la récupération des messages");
        }
    }
}
export function displayOldMessages(room_id, archives) {
    archives.reverse().forEach((msg) => {
        const banned = User.getBanned();
        let data = {
            type: "message",
            room_id,
            message: msg.message,
            sender: msg.author__username,
            date: msg.date,
            id: msg.id,
            modified: msg.modified,
            deleted: msg.deleted,
            users: msg.users
        };
        if (!banned.includes(msg.author__username))
            chat_handler(data);
        else {
            data.message = `${data.sender} has been banned`;
            chat_handler(data);
        }
    });
}
function dices_result(num, face) {
    let result = "( ";
    let results = [];
    let sum = 0;
    for (let i = 0; i < num; i++) {
        results.push(Math.floor(Math.random() * face) + 1);
    }
    sum = results.reduce((acc, val) => acc + val, 0);
    for (let res in results) {
        result += `${results[res]}`;
        if (parseInt(res) === results.length - 1)
            result += ' ';
        else
            result += ', ';
    }
    result += `) = ${sum} !`;
    return result;
}
export function throwDices(data) {
    let message = data.message.slice(6).trim();
    let dices = message.match(/^(\d*)d(\d+)$/);
    let num = 1;
    let faces = 0;
    if (!dices)
        return data.message;
    if (dices && dices[1])
        num = +dices[1];
    if (isNaN(num))
        num = 1;
    if (dices && dices[2])
        faces = +dices[2];
    if (isNaN(faces))
        return data.message;
    if (typeof (num) === "number" && typeof (faces) === "number") {
        let newmessage = `<i>${data.sender} lance ${num} dé${num > 1 ? 's' : ''} ${faces} et obtient ${dices_result(num, faces)}</i>`;
        return (newmessage);
    }
    return data.message;
}
export function actionFormatter(data) {
    let message = data.message;
    if (message.indexOf("/me ") === 0)
        message = `<i>${data.sender} ${message.slice(4)}</i>`;
    if (message.indexOf("/roll ") === 0)
        message = throwDices(data);
    if (message.indexOf("/shout ") === 0)
        message = `${message.slice(7).toUpperCase()}`;
    data.message = message;
    return data;
}
export function setMessage(data) {
    let message = "";
    if (data.modified == true)
        message = `${data.message} <i class="modified_message">modifié</i>`;
    if (data.deleted == true)
        message = `<i class="modified_message">message supprimé</i>`;
    if (!data.modified && !data.deleted)
        message = data.message;
    return message;
}
export function handle_chat_game_request(data) {
    document.body.insertAdjacentHTML('beforeend', `<alert-box alert-msg="${data.message}"
        handler="JOIN_GAME"
        alt-handler="DECLINE_GAME"
        ok_action="JOIN"
        data="${encodeURIComponent(JSON.stringify(data))}"
        cancel_action="DECLINE"
        user="${User.get}"
        action="join_game"    
        friend="${data.player1}"
        class="alert-box">`);
}
export function decline_chat_game(user, operation, data) {
    chat_socket.send(JSON.stringify({
        game_uid: data.game_uid,
        created_by: data.created_by,
        friend: user,
        message: `${user} can't play for the moment`,
        action: operation
    }));
}
export function update_game_alert(message = null) {
    const chat_room = document.getElementById("chatbox");
    const game_alert = document.querySelector(".game-alert");
    if (message) {
        game_alert.textContent = message;
        if (!chat_room.classList.contains("d-none"))
            game_alert.classList.remove("d-none");
    }
    else {
        game_alert.textContent = "No games waiting...";
    }
}
export function notify_game_info(data) {
    update_game_alert(data.message);
    let rooms = getElements("chatmessages");
    rooms.forEach((room) => {
        room.insertAdjacentHTML("beforeend", `<chat-message 
                    class-add = "sender"
                    author-name = "system"
                    date = "${data.date}"
                    msg = "${data.message}"
                    is-user = "false"
                    is-deleted = "false"
                    display-avatar = "false">
                    <strong>GAME INFO : </strong>
                    ${data.message}</chat-message>`);
    });
}
export function chat_handler(data) {
    if (data.type == 'new_avatar') {
        reloadAvatar(data.username);
        if (data.username === User.get()) {
            console.log("NEW AVATAR USER ????");
            // setAvatar()
        }
    }

    if (data.type == 'sync') {
        chat_socket.send(JSON.stringify({ action: "get_users" }));
        updateRooms();
    }
    if (data.type == 'game_info')
        notify_game_info(data);
    if (data.type == 'friend_request') {
        document.body.insertAdjacentHTML('beforeend', `<alert-box
            alert-msg="${data.message}"
            handler="ACCEPT_FRIEND"
            ok_action="ADD"
            cancel_action="REMOVE"
            user="${User.get}"
            friend="${data.friend}"
            class="alert-box">`);
    }
    if (data.type == "game_request")
        handle_chat_game_request(data);
    if (data.type == "decline")
        document.body.insertAdjacentHTML('beforeend', `<alert-box
            alert-msg="${data.message}"
            notify="true"
            class="alert-box">`);
    if (data.type == 'user_list') {
        User.setConnectedUsers(data.users);
        // console.log(User.getConnectedUsers());
        User.setBanned(data.banned);
        setOnlineUsers(data.users, data.friends, data.friend_of, data.banned);
    }
    if (data.type == 'update_message')
        update_message(data);
    if (data.type === 'delete_message')
        update_message(data, DELETE);
    if (data.type == 'message') {
        const banned = User.getBanned();
        let isUser = data.sender === User.get();
        data.date = formatDate(data.date);
        let id = 'chat_' + data.room_id;
        let chatmessages = document.getElementById(id);
        if (banned.includes(data.sender))
            data.message = `${data.sender} has been banned`;
        if (!User.same(data)) {
            chatmessages?.insertAdjacentHTML("beforeend", `<chat-message 
                        class-add = "sender"
                        author-name = "${data.sender}"
                        room_id = "${data.room_id}"
                        msg-id = "${data.id}"
                        date = "${data.date}"
                        msg = "${data.message}"
                        is-user = "${isUser}"
                        is-deleted = "${data.deleted}"
                        display-avatar = "true">
                    <strong>${data.sender}</strong>
                    <span class="chat_date">${data.date}</span><br>
                        <div class="msg-content" room_id="${data.room_id}" msg-id="msg-${data.id}">${setMessage(data)}<div></chat-message>`);
        }
        else
            chatmessages?.insertAdjacentHTML("beforeend", `<chat-message
                        author-name = "${data.sender}"
                        room_id = "${data.room_id}"
                        msg-id = "${data.id}"
                        msg = "${data.message}"
                        date = "${data.date}"
                        is-user="${isUser}"
                        is-deleted = "${data.deleted}"
                        same-user="true"
                        ><div class="msg-content" room_id="${data.room_id}" msg-id="msg-${data.id}">${setMessage(data)}<div></chat-message>`);
        if (chatmessages)
            chatmessages.scrollTop = chatmessages.scrollHeight;
    }
    if (data.type === 'new_message_notification') {
        create_hidded_room(data);
        addRoomSelector(data, 'private', true, true);
        resetChatListeners();
    }
    if (data.type === 'archives') {
        resetChatRoom(data.room_id);
        if (typeof (data.message) === 'string')
            return;
        else {
            displayOldMessages(data.room_id, data.message);
        }
    }
}
export function create_hidded_room(notification, type = "private") {
    let chatwindow = document.querySelector(".chatwindow");
    let newroom = document.querySelector(`chat-room[room_id="${notification.room_id}"]`);
    if (!newroom) {
        chatwindow?.insertAdjacentHTML("beforeend", `<chat-room room_name='${notification.sender}'room_id='${notification.room_id}'></chat-room>`);
        newroom = document.querySelector(`chat-room[room_id="${notification.room_id}"]`);
        if (newroom)
            newroom.classList.add("d-none");
    }
}
export function getConnectedElements() {
    return Array.from(document.getElementsByClassName("connected"));
}
export function getFriendsElements() {
    return Array.from(document.getElementsByClassName("friend_verified"));
}
export function getOpenRoomsBtns() {
    return Array.from(document.getElementsByClassName("room"));
}
export function getOpenRooms() {
    return Array.from(document.getElementsByTagName("chat-room"));
}
export function hideAllRooms() {
    let rooms = getOpenRooms();
    rooms.forEach((room) => {
        room.classList.add("d-none");
    });
}
export function deselectAllRooms() {
    let rooms = getOpenRoomsBtns();
    rooms = [...rooms, ...getFriendsElements()];
    rooms.forEach((room) => {
        room.classList.remove('activeroom');
    });
}
export async function setOnlineUsers(users, friends, friend_of, banned) {
    const userList = document.querySelector(".connected_users");
    const bannedList = document.querySelector(".banned_users");
    const friendsList = document.querySelector(".friends_users");
    resetElement(userList);
    resetElement(bannedList);
    resetElement(friendsList);
    users.forEach((user) => {
        if (user != User.get()) {
            let user_info = dispatchUser(user, users, friends, friend_of);
            if (banned.some((obj) => obj.username === user))
                bannedList.appendChild(getOnlineUser(user_info));
            else {
                if (!friends.includes(user))
                    userList.appendChild(getOnlineUser(user_info));
            }
        }
    });
    friends.forEach((friend) => {
        let user_info = dispatchUser(friend, users, friends, friend_of);
        friendsList.appendChild(getOnlineUser(user_info));
    });
    attachroomcreatelistener(getConnectedElements());
    attachroomcreatelistener(getFriendsElements(), "friend");
}
export function dispatchUser(user, users, friends, friend_of) {
    return {
        user,
        is_friend: friends.includes(user),
        is_connected: users.includes(user),
        is_friend_of: friend_of.includes(user),
        is_banned: User.getBanned().includes(user)
    };
}
function getOnlineUser(user_info) {
    ///// si le user est un ami.... donc récupérer la liste des ami...
    ///// si l'ami est connecté.... l'afficher en connecté si l'amitié est bidirectionnelle
    let user = user_info.user;
    const el = document.createElement("div");
    // if (user_info.is_friend && user_info.is_connected)
    el.classList.add("connected");
    el.innerHTML = user;
    if (!user_info.is_friend && !user_info.is_banned) {
        const add_friend_el = document.createElement("div");
        add_friend_el.classList.add("bi", "bi-person-plus-fill");
        add_friend_el.addEventListener('click', (e) => { userHandler(user, USER_ACTION.ADD); });
        el.appendChild(add_friend_el);
        const ban_el = document.createElement("div");
        ban_el.classList.add("bi", "bi-ban", "ban");
        ban_el.addEventListener('click', (e) => { userHandler(user, USER_ACTION.BAN); });
        el.appendChild(ban_el);
    }
    else if (user_info.is_friend) {
        const friend_el = document.createElement("div");
        const game = document.createElement("div");
        if (user_info.is_friend_of) {
            el.classList.add("friend_verified");
            if (user_info.is_connected) {
                friend_el.classList.add("bi", "bi-person-fill", "text-success");
                game.classList.add("bi", "bi-controller");
                game.addEventListener("click", () => { sendGameRequest(user); });
                el.appendChild(game);
            }
            else
                friend_el.classList.add("bi", "bi-person-fill", "text-secondary");
        }
        else
            friend_el.classList.add("bi", "bi-person-fill", "text-danger");
        friend_el.addEventListener('click', (e) => { userHandler(user, USER_ACTION.REMOVE); });
        el.appendChild(friend_el);
    }
    else if (user_info.is_banned) {
        const unban_el = document.createElement("div");
        unban_el.classList.add("bi", "bi-unlock", "unban");
        unban_el.addEventListener('click', (e) => { userHandler(user, USER_ACTION.UNBAN); });
        el.appendChild(unban_el);
    }
    return el;
}
export function sendGameRequest(friend) {
    let user = User.get();
    if (friend)
        chat_socket.send(JSON.stringify({
            action: "game_request",
            user,
            friend: friend,
            created_by: user,
            game_param: DEFAULT_GAME_PARAMS /// a changer si evolution....
        }));
}
function leaveRoom(roomId) {
    chat_socket.send(JSON.stringify({ action: "leave", room_id: roomId }));
    rooms_ids.delete(roomId);
}
function leaveChannel(roomId) {
    if (chat_socket.readyState === WebSocket.OPEN) {
        if (rooms_ids.has(roomId))
            leaveRoom(roomId);
    }
    else {
        chat_socket.addEventListener("open", () => {
            if (rooms_ids.has(roomId))
                leaveRoom(roomId);
        }, { once: true });
    }
}
function joinRoom(roomId) {
    chat_socket.send(JSON.stringify({ action: "join", room_id: roomId }));
    rooms_ids.add(roomId);
}
function setChannel(roomId) {
    let is_new = !rooms_ids.has(roomId);
    if (chat_socket.readyState === WebSocket.OPEN) {
        if (is_new)
            joinRoom(roomId);
    }
    else {
        chat_socket.addEventListener("open", () => {
            if (is_new)
                joinRoom(roomId);
        }, { once: true });
    }
}
let currentHandler = null;
export function setTextTo(room_id) {
    const chat_text = document.getElementById("chat_text");
    // let previous_room = chat_text.getAttribute("target");
    chat_text?.setAttribute("target", room_id);
    if (currentHandler) {
        chat_text?.removeEventListener('keydown', currentHandler);
    }
    setChannel(room_id);
    currentHandler = (e) => {
        if (e.key === 'Enter') {
            let msg = chat_text.value;
            get_user().then((user) => {
                let message = {
                    action: "message",
                    room_id: chat_text.getAttribute("target") || undefined,
                    sender: user,
                    message: msg
                };
                message = actionFormatter(message);
                chat_socket.send(JSON.stringify(message));
                chat_text.value = "";
            });
        }
    };
    chat_text.addEventListener('keydown', currentHandler);
}
export function createGeneralChatRoom() {
    let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
    const url = getUrl("/chat/create_channel/");
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        credentials: "include",
        body: JSON.stringify({ "type": "general" })
    }).then(res => res.json())
        .then(res => {
        openRoom(res, 'general');
    })
        .catch(err => console.error(err));
}
export function resetChatListeners() {
    let rooms = getOpenRoomsBtns();
    rooms.forEach((room) => {
        room.addEventListener('click', (e) => {
            deselectAllRooms();
            room.classList.add('activeroom');
            let newmessage = room.querySelector(".newmessage");
            if (newmessage)
                room.removeChild(newmessage);
            let opened = getOpenRooms();
            if (opened)
                opened.forEach((o) => {
                    let target = room.getAttribute('target') || "";
                    if (o.id == target) {
                        o.classList.remove("d-none");
                        // o.style.display = "block"
                        setTextTo(target);
                    }
                    else
                        o.classList.add("d-none");
                    //o.style.display = "none";
                });
        });
        room.addEventListener('mouseover', (e) => {
        });
    });
}
export function initChatRoom() {
    createGeneralChatRoom();
    resetChatListeners();
    // setInterval(getOnlineUsers, 5000);
    initEmojis();
    setAvatar();
}
export async function setAvatar() {
    let user = User.get();
    let userinfo = document.querySelector(".userinfo");
    // while (userinfo.firstChild) {
    //     userinfo.removeChild(userinfo.firstChild);
    // }
    // let avatar = document.createElement("img")
    // avatar.classList.add("avatar_image", `${user}_avatar`)
    // userinfo.insertAdjacentElement("beforeend", avatar)
    await getAvatarFromUser(user, userinfo, { height: 96, width: 96, size: "large" });
    const username = document.createElement("div");
    username.innerHTML = user;
    userinfo.insertAdjacentElement("beforeend", username);
}
export function addRoomSelector(chatRoom, type, hide = false, notification = false) {
    //// change chatRoom type
    let activerooms = document.querySelector(".activerooms");
    let target = document.querySelector(`div[target="${chatRoom.room_id}"]`);
    if (!target) {
        let roomSelector;
        if (type === 'private') {
            if (notification === true) {
                roomSelector = `<div class="room" target="${chatRoom.room_id}" close="true">${chatRoom.sender}<div class="newmessage"></div></div>`;
            }
            else
                roomSelector = `<div class="room activeroom" target="${chatRoom.room_id}" close="true">${chatRoom.users[1]}</div>`;
        }
        else
            roomSelector = `<div class="room activeroom" target="${chatRoom.room_id}" close="true">General Chat Room</div>`;
        activerooms?.insertAdjacentHTML("beforeend", roomSelector);
    }
    else if (hide === false)
        target.classList.add("activeroom");
    if (notification === true)
        target?.insertAdjacentHTML("beforeend", `<div class="newmessage"></div>`);
}
export function message_notification(chatRoom) {
    let target = document.querySelector(`div[target="${chatRoom.room_id}"]`);
    let activerooms = document.querySelector(".activerooms");
    if (target && target.classList.contains("activeroom"))
        if (!target) {
            let roomSelector = `<div class="room" target="${chatRoom.room_id}" close="true">${chatRoom.users[1]}
        <div class="newmessage"></div>`;
            activerooms?.insertAdjacentHTML("beforeend", roomSelector);
        }
        else if (!target.classList.contains("activeroom"))
            target.insertAdjacentHTML("beforeend", "<div class='newmessage'></div>");
}
/**
 *
 * @param chatRoom
 * @param type
 */
export function openRoom(chatRoom, type = 'private', el = null) {
    hideAllRooms();
    // console.log("OPEN ROOM DEBUG", chatRoom.room_id)
    let chatwindow = document.querySelector(".chatwindow");
    let newroom = document.querySelector(`chat-room[room_id="${chatRoom.room_id}"]`);
    // console.log(newroom)
    if (!newroom)
        if (type === 'private')
            chatwindow?.insertAdjacentHTML("beforeend", `<chat-room room_name='${chatRoom.users[1]}' room_id='${chatRoom.room_id}'></chat-room>`);
        else if (type === 'friend') {
            chatwindow?.insertAdjacentHTML("beforeend", `<chat-room room_name='${chatRoom.users[1]}' room_id='${chatRoom.room_id}'></chat-room>`);
            newroom = document.querySelector(`chat-room[room_id="${chatRoom.room_id}"]`);
        }
        else if (type === 'general')
            chatwindow?.insertAdjacentHTML("beforeend", `<chat-room room_name='General Chat Room' room_id='${chatRoom.room_id}'></chat-room>`);
        else
            chatwindow?.insertAdjacentHTML("beforeend", `<chat-room room_name='UNKNOWN Chat Room' room_id='${chatRoom.room_id}'></chat-room>`);
    else if (newroom)
        newroom.classList.remove("d-none");
    deselectAllRooms();
    addRoomSelector(chatRoom, type);
    setTextTo(chatRoom.room_id);
    resetChatListeners();
}
export function getRoomFromId(room_id) {
    return document.querySelector(`[room_id="${room_id}"]`);
}
export function resetChatRoom(room_id) {
    const room_element = document.querySelector(`[id="chat_${room_id}"]`);
    resetElement(room_element);
}
export function openFriendRoom(chatRoom, type = 'friend', friend_el = null) {
    if (!friend_el)
        return;
    let target = chatRoom.room_id;
    friend_el.setAttribute("target", target);
}
//attachroomcreatelistener
//openRoom
/**
 *
 * @param users
 *
 * add friends param ???
 *
 *
 */
export function attachroomcreatelistener(users, type = "private") {
    let click = "dblclick";
    if (type === "friend")
        click = "click";
    users.forEach((user) => {
        const banned = User.getBanned();
        user.addEventListener(click, (event) => {
            let receiver = event.target.childNodes[0].textContent;
            let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']")?.value;
            let me = User.get();
            fetch("https://" + window.location.host + "/chat/create_channel/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                credentials: "include",
                body: JSON.stringify({ "type": "private", "username": me, "invited": [me, receiver] })
            }).then(res => res.json())
                .then(res => {
                if (type === 'friend')
                    openFriendRoom(res, type, user);
                openRoom(res, type, user);
            })
                .catch(err => console.error(err));
        });
    });
}
