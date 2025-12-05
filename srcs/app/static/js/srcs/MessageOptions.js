import { displayOldMessages, resetChatRoom, actionFormatter } from "./Chat.js";
import { chat_socket } from "./RegisterSockets.js";
import { User } from "./User.js";
import { editElement, resetElement } from "./dom_utils.js";
import { FIRST } from "./const.js";
export class MessageOptions extends HTMLElement {
    msg_id = "";
    room_id = "";
    constructor() {
        super();
        this.classList.add("msg-options");
        this.msg_id = this.getAttribute("msg-target");
        this.room_id = this.getAttribute("room_id");
        let isUser = this.getAttribute("is-user")?.toLowerCase() === 'true';
        let icon_copy = document.createElement('span');
        icon_copy.classList.add('icons', 'icon-copy');
        this.appendChild(icon_copy);
        icon_copy.addEventListener("click", (event) => {
            if (event.target.parentNode) {
                let text = (event.target.parentElement).parentElement?.getAttribute("msg");
                if (text)
                    navigator.clipboard.writeText(text);
            }
        });
        if (isUser) {
            let pencil = document.createElement('span');
            pencil.classList.add('icons', 'icon-pencil');
            pencil.addEventListener("click", this.changeMessage.bind(this));
            let bin = document.createElement('span');
            bin.classList.add('icons', 'icon-bin');
            bin.addEventListener("click", this.deleteValidation.bind(this));
            this.appendChild(pencil);
            this.appendChild(bin);
        }
    }
    static get observedAttributes() {
        return ['msg-target', 'room_id'];
    }
    ConnectedCallback() {
    }
    DisconnectedCallback() {
    }
    changeMessage(event) {
        let old = "";
        let replace = false;
        let message_el = document.querySelector(`chat-message[msg-id="${this.msg_id}"]`);
        message_el = message_el.querySelector(".msg-content");
        let mod = message_el.querySelector(".modified_message");
        if (mod) {
            mod.remove();
            replace = true;
        }
        if (message_el)
            old = message_el.textContent;
        resetElement(message_el, 1, FIRST);
        message_el.setAttribute("contenteditable", "true");
        editElement(message_el);
        message_el.addEventListener("keydown", edit);
        setTimeout(() => {
            document.addEventListener('click', outclick);
        });
        function outclick(e) {
            e.preventDefault();
            if (!message_el.contains(e.target)) {
                resetListeners();
                if (message_el.textContent !== old) {
                    update_server_message();
                }
                else if (replace)
                    message_el.innerHTML = `${old} <i class="modified_message">modifié</i>`;
            }
        }
        function edit(e) {
            if (e.key === "Enter") {
                e.preventDefault();
                resetListeners();
                if (message_el.textContent !== old) {
                    update_server_message();
                }
                else if (replace)
                    message_el.innerHTML = `${old} <i class="modified_message">modifié</i>`;
            }
            if (e.key === "Escape") {
                e.preventDefault();
                resetListeners();
                message_el.innerHTML = old;
                if (replace)
                    message_el.innerHTML += `<i class="modified_message">modifié</i>`;
            }
        }
        function resetListeners() {
            message_el.setAttribute("contenteditable", "false");
            document.removeEventListener('click', outclick);
            message_el.removeEventListener('keydown', edit);
        }
        function update_server_message() {
            let msg = {
                action: "update_message",
                room_id: message_el.getAttribute("room_id"),
                message_id: message_el.getAttribute("msg-id"),
                sender: User.get(),
                message: message_el.textContent
            };
            msg = actionFormatter(msg);
            chat_socket.send(JSON.stringify(msg));
        }
    }
    deleteValidation(event) {
        const message = document.querySelector(`chat-message[msg-id="${this.msg_id}"]`);
        this.parentElement.addEventListener("continue", this.deleteMessage.bind(this));
        this.parentElement.insertAdjacentHTML("beforeend", `<alert-box alert-msg="This action is irreversible. Are you sure ?"></alert-box>`);
    }
    deleteMessage(event) {
        event.stopImmediatePropagation();
        let msg = {
            action: "delete_message",
            room_id: this.room_id,
            message_id: this.msg_id,
            sender: User.get(),
        };
        chat_socket.send(JSON.stringify(msg));
    }
    reloadRoom(messages) {
        let room_id = messages.room_id;
        resetChatRoom(room_id);
        displayOldMessages(room_id, messages.messages);
    }
    attributeChangedCallback(name, oldValue, newValue) {
        if (name === "msg-target")
            this.msg_id = newValue;
        if (name === "room_id")
            this.room_id = newValue;
    }
}
