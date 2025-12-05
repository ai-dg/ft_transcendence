import { game_alert } from "./GameAlert.js";
export class Cross extends HTMLElement {
    constructor() {
        super();
        let box = document.createElement('div');
        box.classList.add('close-cross');
        this.appendChild(box);
        let line_top = document.createElement('div');
        line_top.classList.add('line-cross', 'line-top');
        let line_bottom = document.createElement('div');
        line_bottom.classList.add('line-cross', 'line-bottom');
        box.appendChild(line_top);
        box.appendChild(line_bottom);
        box.addEventListener('click', () => {
            let target_id = this.getAttribute("target");
            let target = document.getElementById(target_id);
            if (!target)
                target = document.querySelector(`chat-room[room_id='${target_id}']`);
            if (target.classList.contains("d-none"))
                target.classList.remove("d-none");
            else {
                target.classList.add("d-none");
                if (target_id == "chatbox")
                    game_alert?.classList.add("d-none");
            }
        });
    }
    connectedCallback() {
    }
    disconnectedCallback() {
    }
    attributeChangedCallback(name, oldValue, newValue) {
        // console.log(`Attribute ${name} has changed.`);
    }
}
