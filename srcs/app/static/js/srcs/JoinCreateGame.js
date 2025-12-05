import { socket_game } from "./RegisterSockets.js";
import { User } from "./User.js";
import { Game } from "./Game.js";
import { initSocket } from "./Sockets.js";
import { default_map, invited_map, invited_inverted_map } from "./key_map.js";
import { register_game, USER_ACTION } from "./handlers.js";
import { close_windows } from "./uitools.js";
import { display_game_count, display_game_message, display_game_score, clear_all_canvas } from "./GameNotifications.js";
import { game_scene } from "./Scene.js";
import { update_game_alert } from "./Chat.js";
import { updatePills } from "../app.js";
const NEWGAME = "new_game";
const NEWAIGAME = "new_ai_game";
const NEWINVITEDGAME = "new_invited_game";
const NEWTOURNAMENT = "new_tournament";
const ready_btn = document.querySelector(".ready");
const resume_btn = document.querySelector(".resume");
const active_games = {};
export const games_lobby = document.querySelector(".games-lobby");
export let game_socket_is_ready = false;
export let game_socket_outside = null;
export let key_map = default_map;
let countdown_id = null;
let timer = 5;
export function sendMoveCommand(action) {
    if (game_socket_is_ready && game_socket_outside && game_socket_outside.readyState === WebSocket.OPEN) {
        game_socket_outside.send(JSON.stringify({ "action": action }));
    }
}
export function keydown_handler(event) {
    if (`${event.key}` in key_map && key_map[`${event.key}`] !== undefined) {
        sendMoveCommand(key_map[`${event.key}`][0]);
    }
}
export function keyup_handler(event) {
    if (`${event.key}` in key_map && key_map[`${event.key}`] !== undefined) {
        sendMoveCommand(key_map[`${event.key}`][1]);
    }
}
export function update_tournament_lobby(games, add = false) {
    const join_game_list = document.getElementById("tournament_list");
    if (!add)
        join_game_list.innerHTML = "";
    if (games.length === 0)
        if (!add)
            join_game_list.innerHTML = "";
    games.forEach((game) => {
        if (game && game.game_param.opponent == "remote") {
            if (game.players == undefined || game.players == null) {
                game.players = [];
                game.players.push(game.created_by);
            }
            let el = getTournamentElement(game);
            join_game_list.appendChild(el);
        }
    });
}
export function update_game_lobby(games, add = false) {
    const join_game_list = document.getElementById("joingame_list");
    if (!add)
        join_game_list.innerHTML = "";
    games.forEach((game) => {
        if (game && game.game_param.opponent == "remote" && !game.tournament_uid) {
            let el = getGameElement(game);
            join_game_list.appendChild(el);
        }
    });
}
export function update_lobbies(data) {
    update_game_lobby(data.games);
    update_tournament_lobby(data.tournaments);
    if (data.games.length + data.games.tournaments > 0)
        display_game_message("Game or Tournaments are available ! Want to Play ?");
    else
        display_game_message("Please Join or Create a game or Tournament");
}
export function register_tournament(tournament) {
    let tournament_uid = tournament.tournament_uid;
    socket_game.send(JSON.stringify({
        action: "join_tournament",
        tournament_uid,
        tournament_params: tournament.game_params
    }));
}
function getGameElement(game) {
    let el = document.getElementById(game.game_uid);
    if (!el) {
        el = document.createElement("div");
        el.classList.add("container", "d-flex");
        el.id = game.game_uid;
        let gameinfo_box_2 = document.createElement('div');
        gameinfo_box_2.classList.add("container", "text-light", "mt-4", "p-3", "border");
        el.appendChild(gameinfo_box_2);
        let slots = document.createElement('h6');
        slots.innerHTML = "Players: 1 / 2 - " + game.created_by;
        gameinfo_box_2.appendChild(slots);
        let winCondition = document.createElement('h6');
        winCondition.innerHTML = "Win condition: " + game.game_param.win_condition + " / " + game.game_param.max_pts + " pts";
        gameinfo_box_2.appendChild(winCondition);
        let owner = document.createElement('h6');
        owner.innerHTML = "Owner: " + game.created_by;
        gameinfo_box_2.appendChild(owner);
        let join_btn = document.createElement('button');
        join_btn.classList.add("btn", "btn-success", "mt-4");
        join_btn.type = "button";
        join_btn.innerHTML = "Join game";
        if (game.created_by != User.get())
            gameinfo_box_2.appendChild(join_btn);
        join_btn.addEventListener("click", () => {
            close_windows();
            register_game(User.get(), USER_ACTION.NONE, game);
        });
        if (game.created_by == User.get()) {
            let delete_btn = document.createElement('button');
            delete_btn.classList.add("btn", "btn-danger", "mt-4");
            delete_btn.type = "button";
            delete_btn.innerHTML = "Delete";
            gameinfo_box_2.appendChild(delete_btn);
            delete_btn.addEventListener("click", () => {
                close_windows();
                let data = {
                    action: "canceled_game",
                    game_uid: game.game_uid,
                };
                socket_game.send(JSON.stringify(data));
                remove_game(game.game_uid);
            });
        }
    }
    return el;
}
export function update_game_display(game) {
    let el = getTournamentElement(game[0]);
    el.remove();
}
export function remove_game(game_uid) {
    let game = document.getElementById(game_uid);
    if (game)
        game.parentNode?.removeChild(game);
    updatePills();
}
export function update_tournament_display(game) {
    game = game[0];
    console.log(game);
    let el = getTournamentElement(game);
}
async function send_ready_state(socket, el) {
    socket.send(JSON.stringify({ command: "start" }));
}
export function display_action_button(socket, btn) {
    const handleReadyClick = async (e) => {
        await send_ready_state(socket, btn);
        btn.removeEventListener("click", handleReadyClick);
        update_game_alert();
        btn.classList.add("d-none");
    };
    btn.classList.remove("d-none");
    btn.addEventListener("click", handleReadyClick);
}
export function launch(params, game_socket_id) {
    if (game_socket_id) {
        if (params.status === "game_ready") {
            display_action_button(game_socket_id, ready_btn);
            clear_all_canvas();
            display_game_message(`All players connected ! Press Ready to start !`);
        }
        else {
            if (!ready_btn.classList.contains("d-none"))
                ready_btn.classList.add("d-none");
            display_action_button(game_socket_id, resume_btn);
        }
    }
}
export async function play(params) {
    let game_socket_id = null;
    if (active_games[params.game_uid]) {
        game_socket_id = active_games[params.game_uid];
        launch(params, game_socket_id);
        //console.log("✅ Game WebSocket connected --- GAME SOCKET ALREADY EXISTS - NO SOCKET IS CREATED")
    }
    else {
        game_socket_id = initSocket(`/ws/pong/${params.game_uid}`);
        game_socket_id.onopen = () => {
            console.log("✅ Game WebSocket connected!");
            game_socket_is_ready = true;
            game_socket_outside = game_socket_id;
            if (game_socket_id) {
                active_games[params.game_uid] = game_socket_id;
                launch(params, game_socket_id);
            }
        };
        game_socket_id.onmessage = (event) => run(event, game_socket_id);
        game_socket_id.onerror = (event) => console.log("❌ WebSocket error:", event);
        game_socket_id.onclose = () => {
            console.log("🔴 Test WebSocket disconnected!");
            game_socket_is_ready = false;
            game_socket_outside = null;
            delete active_games[params.game_uid];
            unset_game_listeners();
        };
        let opponent = params.game_param.opponent;
        let left = params.left === opponent;
        key_map = default_map;
        if (opponent === 'invited' && left)
            key_map = invited_inverted_map;
        if (opponent === 'invited' && !left)
            key_map = invited_map;
    }
    ;
}
export function set_game_listeners() {
    document.addEventListener("keydown", keydown_handler);
    document.addEventListener("keyup", keyup_handler);
}
export function unset_game_listeners() {
    document.removeEventListener("keydown", keydown_handler);
    document.removeEventListener("keyup", keyup_handler);
}
let data_game = null;
let lastUpdate = Date.now();
export function cancel_countdown() {
    if (countdown_id)
        clearInterval(countdown_id);
}
function countdown() {
    if (!countdown_id)
        return;
    game_scene.clear();
    if (timer > 0)
        display_game_count(`${timer}`, false);
    if (timer == 0)
        display_game_count(`Ready ?`, false);
    if (timer == -1) {
        display_game_count(`Go !`, false);
    }
    if (timer == -2) {
        if (game_socket_outside)
            game_socket_outside.send(JSON.stringify({ command: "go" }));
        cancel_countdown();
        countdown_id = null;
        set_game_listeners();
        timer--;
        return;
    }
    timer--;
}
export async function run(event, game_socket_id) {
    let now = Date.now();
    data_game = JSON.parse(event.data);
    if (data_game.status == "init") {
        clear_all_canvas();
        display_game_score(data_game);
    }
    else if (data_game.status === "resume") {
        if (window.gameInstance)
            window.gameInstance.stop();
        cancel_countdown();
        display_game_message(`All players reconnected ! Press Resume to resume the game !`);
    }
    else if (data_game.status == "start_count") {
        timer = 5;
        countdown_id = setInterval(countdown, 1000);
    }
    else if (data_game.status && data_game.status == "running") {
        if (countdown_id)
            cancel_countdown();
        lastUpdate = now;
        if (window.gameInstance) {
            window.gameInstance.start();
            window.gameInstance.updateGame(data_game);
        }
        else {
            console.log("🎮 Creating a new game instance!");
            window.gameInstance = new Game(data_game);
        }
    }
    else if (data_game.status == "end_game" || data_game.type == "end_game") {
        console.log("IN GAMESOCKET FUCKING CONDITIONNNNNN !!!!!");
        game_socket_id.close(1000);
        if (window.gameInstance) {
            window.gameInstance.stop();
            window.gameInstance = null;
        }
        display_game_score(data_game);
        if (data_game.action != "none") {
            if (data_game.winner === User.get()) {
                if (!data_game.tournament_uid)
                    display_game_message("You win the game ! Please wait for your opponent");
                display_game_message("You win the game !");
            }
            else {
                display_game_message(`Game Over, ${data_game.winner} win the game !`);
            }
        }
    }
    // else
    //     console.log(data_game);
}
function format_players(players) {
    let str = "";
    for (let i = 0; i < players.length; i++) {
        str += players[i];
        if (i < players.length - 1)
            str += ", ";
    }
    return str;
}
function getTournamentElement(game) {
    let el = document.getElementById(game.tournament_uid);
    if (!el) {
        el = document.createElement("div");
        el.classList.add("container", "d-flex");
        el.id = game.tournament_uid;
        let gameinfo_box_2 = document.createElement('div');
        gameinfo_box_2.classList.add("container", "text-light", "mt-4", "p-3", "border", "gameinfo");
        el.appendChild(gameinfo_box_2);
        let slots = document.createElement('h6');
        slots.classList.add("slots");
        slots.innerHTML = "Players: " + game.players.length + " / " + game.expected + " - " + format_players(game.players);
        gameinfo_box_2.appendChild(slots);
        let winCondition = document.createElement('h6');
        winCondition.innerHTML = "Win condition: " + game.game_param.win_condition + " / " + game.game_param.max_pts + " pts";
        gameinfo_box_2.appendChild(winCondition);
        let owner = document.createElement('h6');
        owner.classList.add("owner");
        owner.innerHTML = "Owner: " + game.created_by;
        gameinfo_box_2.appendChild(owner);
        let join_btn = document.createElement('button');
        join_btn.classList.add("btn", "btn-success", "mt-4", "join");
        join_btn.type = "button";
        join_btn.innerHTML = "Join game";
        if (game.created_by != User.get()) {
            gameinfo_box_2.appendChild(join_btn);
            join_btn.addEventListener("click", () => {
                close_windows();
                register_tournament(game);
            });
        }
        if (game.created_by == User.get()) {
            let delete_btn = document.createElement('button');
            delete_btn.classList.add("btn", "btn-danger", "mt-4");
            delete_btn.type = "button";
            delete_btn.innerHTML = "Delete";
            gameinfo_box_2.appendChild(delete_btn);
            delete_btn.addEventListener("click", () => {
                close_windows();
                let data = {
                    action: "canceled_tournament",
                    game_uid: game.tournament_uid,
                };
                socket_game.send(JSON.stringify(data));
                remove_game(game.tournament_uid);
            });
        }
    }
    else {
        if (game.players) {
            let slots = el.querySelector(".slots");
            slots.innerHTML = "Players: " + game.players.length + " / " + game.expected + " - " + format_players(game.players);
            let join = el.querySelector(".gameinfo").querySelector(".join");
            if (game.players.includes(User.get())) {
                if (join && join.parentElement)
                    join.parentElement?.removeChild(join);
            }
        }
    }
    return el;
}
