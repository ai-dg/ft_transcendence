import { userHandler, USER_ACTION } from "./handlers.js";
import { register_game } from "./handlers.js";
import { decline_chat_game } from "./Chat.js";
export const ALERT_ACTIONS = Object.freeze({
    ACCEPT_FRIEND: userHandler,
    REJECT_FRIEND: userHandler,
    JOIN_GAME: register_game,
    DECLINE_GAME: decline_chat_game
});
export class Alert extends HTMLElement {
    // notify = "true"
    // ok_action= " abort"
    // data="${JSON.stringify(data)}"
    // class="alert-box">`)
    constructor() {
        super();
        let notify = this.getAttribute("notify") == "true";
        let ok_action = this.getAttribute("ok_action");
        let cancel_action = this.getAttribute("cancel_action");
        let handler = this.getAttribute("handler");
        let alt_handler = null;
        if (this.getAttribute("alt-handler"))
            alt_handler = this.getAttribute("alt-handler");
        let user = this.getAttribute("user");
        let friend = this.getAttribute("friend");
        let data = this.getAttribute("data");
        if (data)
            data = JSON.parse(decodeURIComponent(data));
        else
            data = {};
        this.classList.add("alert-box");
        const alertbtn = document.createElement("div");
        alertbtn.classList.add("alert-btn", "d-flex", "gap-3");
        const okbtn = document.createElement("div");
        okbtn.innerText = "Ok";
        okbtn.classList.add("btn", "action_button", "black", "text-light", "mb-3");
        alertbtn.appendChild(okbtn);
        if (!notify) {
            const cancelbtn = document.createElement("div");
            cancelbtn.innerText = "Cancel";
            cancelbtn.classList.add("btn", "action_button", "black", "text-light", "mb-3");
            if (handler) {
                okbtn.addEventListener("click", () => {
                    ALERT_ACTIONS[handler](friend, USER_ACTION[ok_action], data);
                    this.remove();
                });
                cancelbtn.addEventListener("click", () => {
                    if (alt_handler)
                        ALERT_ACTIONS[alt_handler](friend, USER_ACTION[cancel_action], data);
                    else
                        ALERT_ACTIONS[handler](friend, USER_ACTION[cancel_action], data);
                    this.remove();
                });
            }
            else {
                okbtn.addEventListener("click", this.continue.bind(this));
                cancelbtn.addEventListener("click", this.abort.bind(this));
            }
            alertbtn.appendChild(cancelbtn);
        }
        else
            okbtn.addEventListener("click", this.continue.bind(this));
        const message = document.createElement("div");
        message.classList.add("alert-msg");
        message.innerText = this.getAttribute("alert-msg");
        this.appendChild(message);
        this.appendChild(alertbtn);
    }
    continue() {
        let continue_sig = new CustomEvent("continue", { bubbles: true });
        this.dispatchEvent(continue_sig);
        this.remove();
    }
    abort() {
        let abort_sig = new CustomEvent("abort", { bubbles: true });
        this.dispatchEvent(abort_sig);
        this.remove();
    }
}
