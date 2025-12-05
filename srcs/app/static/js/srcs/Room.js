export class Room extends HTMLElement {
    id = "";
    invited = [];
    roomname = document.createElement('div');
    constructor() {
        super();
        let title = this.getAttribute("room_name");
        this.roomname.classList.add("room_name");
        if (title.length != 0)
            this.roomname.innerHTML += title;
        this.appendChild(this.roomname);
        let chatmessages = document.createElement('div');
        this.id = this.getAttribute("room_id");
        this.roomname.innerHTML += `<cross-element target="${this.id}"></cross-element>`;
        chatmessages.classList.add('chatmessages');
        chatmessages.id = 'chat_' + this.id;
        this.appendChild(chatmessages);
    }
    static get observedAttributes() {
        return ['room_id', 'id'];
    }
    connectedCallback() {
    }
    attributeChangedCallback(name, oldValue, newValue) {
    }
    disconnectedCallback() {
        // console.log("Disconnected room")
    }
    invite_user(user) {
        this.invited.push(user);
    }
    remove_user(user) {
    }
}
