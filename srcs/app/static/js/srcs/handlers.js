import { User } from "./User.js";
import { chat_socket, socket_game } from "./RegisterSockets.js";
export const USER_ACTION = Object.freeze({
    ADD: "add_friend",
    REMOVE: "remove_friend",
    BAN: "ban",
    UNBAN: "unban",
    NONE: "none",
    JOIN: "join_game",
    DECLINE: "decline"
});
/**
 * handler function for the alert custom element,
 * that passes a fonction to handle case for ok and cancel buttons handled by action
 *
 * @param user : string username of the target of the operation
 * @param operation from ALERT_ACTIONS - in this case, can be ACCEPT_FRIEND or REJECT_FRIEND
 */
export async function userHandler(user, operation) {
    let action = "none";
    if (Object.values(USER_ACTION).includes(operation))
        action = operation;
    let back = {
        action,
        sender: User.get(),
        user
    };
    if (action != "none")
        chat_socket.send(JSON.stringify(back));
    else
        (console.error("Wrong action type !"));
}
export function register_game(user, operation, game) {
    let game_uid = game.game_uid;
    socket_game.send(JSON.stringify({
        action: "join_game",
        game_uid,
        game_params: game.game_params
    }));
}
