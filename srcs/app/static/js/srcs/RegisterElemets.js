import { Alert } from "./Alert.js";
import { Avatar } from "./Avatars.js";
import { ChatMessage } from "./ChatMessage.js";
import { Cross } from "./Cross.js";
import { MessageOptions } from "./MessageOptions.js";
import { Room } from "./Room.js";
import { Fold } from "./FoldElement.js";
export function registerElements() {
    customElements.define('fold-element', Fold);
    customElements.define('cross-element', Cross);
    customElements.define('chat-room', Room);
    customElements.define('message-options', MessageOptions);
    customElements.define('chat-message', ChatMessage);
    customElements.define('alert-box', Alert);
    customElements.define('avatar-element', Avatar);
}
