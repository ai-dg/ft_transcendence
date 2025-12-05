import { getAvatarFromUser } from "./Avatars.js";
import { extractHour } from "./Date.js";
export class ChatMessage extends HTMLElement {
    sender = "";
    isUser = false;
    msg_id = "";
    date = "";
    author_name = "";
    optionselement = null;
    dateelement = null;
    message = "";
    room_id = "";
    display_avatar = false;
    is_deleted = false;
    constructor() {
        super();
        this.classList.add("msg");
        let class_add = this.getAttribute("class-add");
        if (class_add)
            this.classList.add(class_add);
        this.display_avatar = this.getAttribute("display-avatar") === "true";
        this.isUser = this.getAttribute("is-user") === "true";
        this.room_id = this.getAttribute("room_id");
        this.msg_id = this.getAttribute("msg-id");
        this.is_deleted = this.getAttribute("is-deleted") === "true";
        let msg = this.getAttribute("msg");
        if (msg)
            this.message = msg;
        this.date = this.getAttribute("date");
        this.author_name = this.getAttribute("author-name");
    }
    static get observedAttributes() {
        return ['sender', 'room_id', 'display-avatar'];
    }
    createMessageOptions() {
        this.insertAdjacentHTML("beforeend", `<message-options room_id="${this.room_id}" msg-target="${this.msg_id}" is-user="${this.isUser}"></message-options>`);
        this.optionselement = this.querySelector("message-options");
        if (!this.display_avatar) {
            this.insertAdjacentHTML("beforeend", `<div class="message_date">${extractHour(this.date)}</div>`);
            this.dateelement = this.querySelector(".message_date");
        }
    }
    attachListeners() {
        this.addEventListener('mouseover', () => {
            this.optionselement.style.display = "flex";
            if (!this.display_avatar)
                this.dateelement.style.display = "block";
        });
        this.addEventListener('mouseleave', () => {
            this.optionselement.style.display = "none";
            if (!this.display_avatar)
                this.dateelement.style.display = "none";
        });
    }
    async connectedCallback() {
        let msg = this.getAttribute("msg");
        if (msg)
            this.message = msg;
        this.author_name = this.getAttribute("author-name");
        if (this.display_avatar) {
            const avatar_wrap = document.createElement("div");
            avatar_wrap.classList.add("avatar-msg-wrap");
            this.appendChild(avatar_wrap);
            try {
                await getAvatarFromUser(this.author_name, avatar_wrap, { height: 32, width: 32, size: "small" });
            }
            catch (err) {
                console.error("Failed to load avatar:", err);
            }
        }
        if (!this.is_deleted) {
            const msgoptions = this.createMessageOptions();
            this.attachListeners();
        }
    }
    disconnectedCallback() {
    }
    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'room_id')
            this.room_id = newValue;
        if (name === 'display-avatar')
            this.display_avatar = newValue === 'true';
    }
}
