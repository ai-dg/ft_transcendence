import { initChatRoom } from "./srcs/Chat.js";
import { User } from "./srcs/User.js";
import { initUserInfo, updateUser } from "./srcs/User.js";
import { registerElements } from "./srcs/RegisterElemets.js";
import { socket_game } from "./srcs/RegisterSockets.js";
import { update_game_lobby, play, update_lobbies, update_tournament_lobby, update_tournament_display, unset_game_listeners, game_socket_outside } from "./srcs/JoinCreateGame.js";
import { display_game_message } from "./srcs/GameNotifications.js";
import { close_windows, color_canvas, count_child_nodes, hide_pill, notification_message, PILLS, show_pill } from "./srcs/uitools.js";
import { play_tournament } from "./srcs/JoinCreateTournament.js";
import { remove_game } from "./srcs/JoinCreateGame.js";
import { default_map, invited_map, invited_inverted_map } from "./srcs/key_map.js";
import { getCSRFToken } from "./srcs/Security.js";
import { formatDate } from "./srcs/Date.js";
import { cancel_countdown } from "./srcs/JoinCreateGame.js";
import { game_alert } from "./srcs/GameAlert.js";
import { update_game_alert } from "./srcs/Chat.js";
registerElements();
let status = false; // not used yet...
let data_game = null;
window.gameInstance = null;
let lastUpdate = Date.now();
export let isSocketReady = false;
const join_tournament_list = document.getElementById("tournament_list");
const join_game_list = document.getElementById("joingame_list");
/// a chaque chargement de page
/// a chaque remove
export function updatePills() {
    let avail_tournaments = count_child_nodes(join_tournament_list);
    let avail_games = count_child_nodes(join_game_list);
    let all = avail_tournaments + avail_games;
    if (avail_tournaments)
        show_pill(PILLS.TOURNAMENTS, avail_tournaments);
    else
        hide_pill(PILLS.TOURNAMENTS);
    if (avail_games)
        show_pill(PILLS.GAMES, avail_games);
    else
        hide_pill(PILLS.GAMES);
    if (all)
        show_pill(PILLS.ALLGAMES, all);
    else
        hide_pill(PILLS.ALLGAMES);
}
socket_game.onopen = () => {
    console.log("✅ [app.ts] WebSocket (Game) connected!");
    isSocketReady = true;
};
let GAMES = [];
let TOURNAMENTS = [];
let MY_GAMES = [];
let player_statistics = {
    total_games_played: 0,
    total_games_wons: 0,
    total_points_scored: 0,
    total_points_conceded: 0,
    total_tournaments_played: 0,
    total_tournaments_won: 0,
};
socket_game.onmessage = (event) => {
    let now = Date.now();
    let response = JSON.parse(event.data);
    // console.log(`socket GAME_LOBBY data receive : ${event.data}`);
    if (response.status === "disconnect") {
        if (window.gameInstance) {
            window.gameInstance.stop();
            window.gameInstance = null;
        }
        cancel_countdown();
        unset_game_listeners();
        /*
        if (game_socket_outside)
          game_socket_outside.close(1000)*/
        display_game_message(`Your opponent leaved the game ! Please wait !`);
    }
    if (response.status === "game_paused")
        update_game_alert("A neu game is ready ! Please join the arena");
    if (response.status === "init_lobby") {
        update_lobbies(response);
        updatePills();
    }
    if (response.status === "game_created") {
        if (!game_socket_outside)
            display_game_message("A new game is available");
        update_game_lobby([response], true);
        updatePills();
    }
    if (response.status === "tournament_created") {
        if (!game_socket_outside)
            display_game_message("A new tournament is available");
        update_tournament_lobby([response], true);
        updatePills();
    }
    if (response.status === "join_tournament") {
        update_tournament_display([response]);
    }
    if (response.status === "tournament_ready") {
        remove_game(response.tournament_uid);
        play_tournament(response);
    }
    if (response.type === "send_game_announcement") {
        if (response.created_by === User.get()) {
            display_game_message(response.message);
        }
    }
    if (response.status === "game_deleted" || response.status === "tournament_deleted" || response.status === "remove_game" || response.status === "tournament_game") {
        remove_game(response.game_uid);
    }
    if (response.status === "game_ready" || response.status === "in_progress") {
        remove_game(response.game_uid);
        play(response);
    }
};
socket_game.onerror = (event) => console.log("❌ [app.ts] WebSocket error:", event);
socket_game.onclose = () => {
    console.log("🔴 [app.ts] WebSocket disconnected!");
    isSocketReady = false;
};
document.addEventListener("DOMContentLoaded", () => {
    console.log("📌 DOM loaded, initializing the game...");
    const logoutButton = document.querySelector("#logout");
    // const stopGameButton = document.getElementById("stop_game");
    const newGameButton = document.getElementById("new_game");
    const joinGameButton = document.getElementById("join_game");
    const BestScoreButton = document.getElementById("best_scores");
    const chatButton = document.getElementById("chat");
    const accountButton = document.getElementById("account");
    const submitUserInfosButton = document.getElementById("submit-user-infos");
    color_canvas();
    if (newGameButton) {
        newGameButton.addEventListener("click", () => {
            let target = document.getElementById("NewGameWrapper");
            if (target.classList.contains("d-none")) {
                close_windows();
                target.classList.remove("d-none");
            }
            else
                target.classList.add("d-none");
        });
    }
    if (BestScoreButton) {
        BestScoreButton.addEventListener("click", () => {
            let target = document.getElementById("BestScoreWrapper");
            if (target.classList.contains("d-none")) {
                close_windows();
                (async () => {
                    loadPlayerStatistics(User.get());
                    loadPlayerHistory(User.get());
                })();
                target.classList.remove("d-none");
                let titlebestscore = document.getElementById("bestScoreTitle");
                titlebestscore.innerText = "Best Score";
            }
            else
                target.classList.add("d-none");
        });
    }
    if (joinGameButton) {
        joinGameButton.addEventListener("click", () => {
            let target = document.getElementById("JoinGameWrapper");
            if (target.classList.contains("d-none")) {
                // UpdateGameList(GAMES);
                close_windows();
                target.classList.remove("d-none");
                const join_game_list = document.getElementById("joingame_list");
                if (join_game_list.childElementCount <= 0) {
                    no_games_text.classList.remove("d-none");
                    no_games_text.innerHTML = "No games available";
                }
                else {
                    no_games_text.classList.add("d-none");
                }
            }
            else
                target.classList.add("d-none");
        });
    }
    let keyboardButton = document.getElementById("keyboard");
    if (keyboardButton) {
        keyboardButton.addEventListener("click", () => {
            let target = document.getElementById("KeyboardWrapper");
            if (target.classList.contains("d-none")) {
                close_windows();
                target.classList.remove("d-none");
                loadKeyButtons();
            }
            else
                target.classList.add("d-none");
        });
    }
    // JOIN PART FILTER BUTTON 
    const player_vs_player_filter_btn = document.getElementById("btnradio2");
    const tournament_filter_btn = document.getElementById("btnradio3");
    const join_tournament_list = document.getElementById("tournament_list");
    const join_game_list = document.getElementById("joingame_list");
    const history_game_btn = document.getElementById("historybtn");
    const history_container = document.getElementById("history_games");
    const player_statistics_container = document.getElementById("player_stats");
    const no_games_text = document.getElementById("no-games");
    if (history_game_btn) {
        history_game_btn.addEventListener("click", () => {
            if (history_container.classList.contains("d-none")) {
                player_statistics_container.classList.add("d-none");
                history_container.classList.remove("d-none");
                history_game_btn.textContent = "Hide game history";
            }
            else {
                player_statistics_container.classList.remove("d-none");
                history_container.classList.add("d-none");
                history_game_btn.textContent = "Show game history";
            }
        });
    }
    if (player_vs_player_filter_btn) {
        player_vs_player_filter_btn.addEventListener("click", () => {
            join_tournament_list.classList.add("d-none");
            join_game_list.classList.remove("d-none");
            if (join_game_list.childElementCount <= 0) {
                no_games_text.classList.remove("d-none");
                no_games_text.innerHTML = "No games available";
            }
            else {
                no_games_text.classList.add("d-none");
            }
        });
    }
    if (tournament_filter_btn) {
        tournament_filter_btn.addEventListener("click", () => {
            join_game_list.classList.add("d-none");
            join_tournament_list.classList.remove("d-none");
            if (join_tournament_list.childElementCount <= 0) {
                no_games_text.classList.remove("d-none");
                no_games_text.innerHTML = "No tournaments available";
            }
            else {
                no_games_text.classList.add("d-none");
            }
        });
    }
    // if (stopGameButton) {
    //     stopGameButton.addEventListener("click", () => {
    //         console.log("🟢 'Stop Game' button clicked, sending STOP command...");
    //         sendStopCommand();
    //     });
    // }
    if (logoutButton) {
        logoutButton.addEventListener("click", () => window.location.href = "accounts/logout/");
    }
    submitUserInfosButton.addEventListener("click", async (event) => {
        try {
            await updateUser();
            let target = document.getElementById("userDetailsWrapper");
            target.classList.add("d-none");
        }
        catch {
            console.error("User Update error");
        }
    });
    // SETTINGS GAME PART
    const easy = document.getElementById("easy");
    const medium = document.getElementById("medium");
    const hard = document.getElementById("hard");
    const impossible = document.getElementById("impossible");
    let old_btn_difficulty = hard;
    let difficulty = 'hard';
    easy.addEventListener("click", (event) => {
        difficulty = 'easy';
        if (old_btn_difficulty) {
            if (old_btn_difficulty.classList.contains("btn_selected"))
                old_btn_difficulty.classList.remove("btn_selected");
        }
        if (!easy.classList.contains("btn_selected"))
            easy.classList.add("btn_selected");
        old_btn_difficulty = easy;
    });
    medium.addEventListener("click", (event) => {
        difficulty = 'medium';
        if (old_btn_difficulty) {
            if (old_btn_difficulty.classList.contains("btn_selected"))
                old_btn_difficulty.classList.remove("btn_selected");
        }
        if (!medium.classList.contains("btn_selected"))
            medium.classList.add("btn_selected");
        old_btn_difficulty = medium;
    });
    hard.addEventListener("click", (event) => {
        difficulty = 'hard';
        if (old_btn_difficulty) {
            if (old_btn_difficulty.classList.contains("btn_selected"))
                old_btn_difficulty.classList.remove("btn_selected");
        }
        if (!hard.classList.contains("btn_selected"))
            hard.classList.add("btn_selected");
        old_btn_difficulty = hard;
    });
    impossible.addEventListener("click", (event) => {
        difficulty = 'impossible';
        if (old_btn_difficulty) {
            if (old_btn_difficulty.classList.contains("btn_selected")) {
                old_btn_difficulty.classList.remove("btn_selected");
            }
        }
        if (!impossible.classList.contains("btn_selected"))
            impossible.classList.add("btn_selected");
        old_btn_difficulty = impossible;
    });
    accountButton.addEventListener("click", (event) => {
        let target = document.getElementById("userDetailsWrapper");
        if (target.classList.contains("d-none")) {
            close_windows();
            target.classList.remove("d-none");
        }
        else
            target.classList.add("d-none");
    });
    chatButton.addEventListener("click", (event) => {
        let target = document.querySelector(".chatbox");
        if (target.classList.contains("d-none")) {
            close_windows();
            target.classList.remove("d-none");
            game_alert?.classList.remove("d-none");
        }
        else {
            target.classList.add("d-none");
            game_alert?.classList.add("d-none");
        }
    });
    const maxpts_input = document.getElementById("input-maxpts");
    const wincondition_input = document.getElementById("win-condition");
    let max_pts_value = maxpts_input.value;
    let wincondition_value = wincondition_input.value;
    function sendCreateCommand(action) {
        if (isSocketReady && socket_game.readyState === WebSocket.OPEN) {
            let data = { action, user: User.get() };
            switch (action) {
                case NEWGAME:
                    data["game_param"] = { opponent: "remote", player: 2, max_pts: max_pts_value, win_condition: wincondition_value, level: "none" };
                    break;
                case NEWAIGAME:
                    data["game_param"] = { opponent: "ai", player: 2, max_pts: max_pts_value, win_condition: wincondition_value, level: difficulty };
                    break;
                case NEWINVITEDGAME:
                    data["game_param"] = { opponent: "invited", player: 2, max_pts: max_pts_value, win_condition: wincondition_value, level: "none" };
                    break;
                case NEWTOURNAMENT:
                    console.log("tournament......");
                    data["game_param"] = { opponent: "remote", player: 4, max_pts: max_pts_value, win_condition: wincondition_value, level: "none" };
                    break;
                default:
                    data["game_params"] = {};
                    console.log("invalid game creation request");
                    return; // 
            }
            socket_game.send(JSON.stringify(data));
        }
    }
    // NEW GAME PART
    const NEWGAME = "new_game";
    const NEWAIGAME = "new_ai_game";
    const NEWINVITEDGAME = "new_invited_game";
    const NEWTOURNAMENT = "new_tournament";
    const player_vs_ia = document.getElementById("gm_btn_1");
    const player_vs_player = document.getElementById("gm_btn_2");
    const tournament = document.getElementById("gm_btn_3");
    const player_vs_invited = document.getElementById("gm_btn_4");
    const create_game = document.getElementById("create_game");
    const iasettings = document.querySelector(".aisettings");
    let old_btn = player_vs_ia;
    let gamemode_selected = 1;
    player_vs_ia.addEventListener("click", (event) => {
        gamemode_selected = 1;
        if (old_btn) {
            if (old_btn.classList.contains("btn_selected"))
                old_btn.classList.remove("btn_selected");
        }
        if (iasettings.classList.contains("d-none"))
            iasettings.classList.remove("d-none");
        if (!player_vs_ia.classList.contains("btn_selected"))
            player_vs_ia.classList.add("btn_selected");
        old_btn = player_vs_ia;
    });
    player_vs_player.addEventListener("click", (event) => {
        gamemode_selected = 2;
        if (old_btn) {
            if (old_btn.classList.contains("btn_selected"))
                old_btn.classList.remove("btn_selected");
        }
        if (!player_vs_player.classList.contains("btn_selected"))
            player_vs_player.classList.add("btn_selected");
        old_btn = player_vs_player;
        iasettings.classList.add("d-none");
    });
    tournament.addEventListener("click", (event) => {
        gamemode_selected = 3;
        if (old_btn) {
            if (old_btn.classList.contains("btn_selected"))
                old_btn.classList.remove("btn_selected");
        }
        if (!tournament.classList.contains("btn_selected"))
            tournament.classList.add("btn_selected");
        old_btn = tournament;
        iasettings.classList.add("d-none");
    });
    player_vs_invited.addEventListener("click", (event) => {
        gamemode_selected = 4;
        if (old_btn) {
            if (old_btn.classList.contains("btn_selected"))
                old_btn.classList.remove("btn_selected");
        }
        if (!player_vs_invited.classList.contains("btn_selected")) {
            player_vs_invited.classList.add("btn_selected");
        }
        old_btn = player_vs_invited;
        iasettings.classList.add("d-none");
    });
    function verify_gameoptions(maxpts_input, wincondition_input) {
        const maxptsinput_int = parseInt(maxpts_input);
        const win_condition_int = parseInt(wincondition_input);
        if (isNaN(maxptsinput_int) || isNaN(win_condition_int))
            return false;
        if (maxptsinput_int < 1 || win_condition_int < 1)
            return false;
        return true;
    }
    let loop_id = null;
    create_game.addEventListener("click", (event) => {
        if (isSocketReady && socket_game.readyState === WebSocket.OPEN) {
            let action = "new_ai_game";
            close_windows();
            switch (gamemode_selected) {
                case 1:
                    action = "new_ai_game";
                    break;
                case 2:
                    action = "new_game";
                    break;
                case 3:
                    action = "new_tournament";
                    break;
                case 4:
                    action = "new_invited_game";
                    break;
                default:
                    action = "new_ai_game";
                    console.log("invalid gamemode");
                    return;
            }
            max_pts_value = maxpts_input.value;
            wincondition_value = wincondition_input.value;
            if (!verify_gameoptions(max_pts_value, wincondition_value)) {
                notification_message("Invalid input");
                return;
            }
            sendCreateCommand(action);
            if (loop_id)
                clearTimeout(loop_id);
            loop_id = null;
        }
        else {
            console.warn("⚠️ WebSocket not ready");
        }
    });
});
// function sendStopCommand() {
//     if (isSocketReady && socket_game.readyState === WebSocket.OPEN) {
//         console.log("🚀 Sending STOP command to the server...");
//         socket_game.send(JSON.stringify({ "command": "stop" }));
//     } else {
//         console.warn("⚠️ WebSocket is not ready yet, retrying...");
//         setTimeout(sendStopCommand, 500);
//     }
// }
function getKeyMaps() {
    fetch("/accounts/keymap/?user=" + User.get())
        .then(response => response.json())
        .then(data => {
        if (data.default_map) {
            for (const key in default_map)
                delete default_map[key];
            Object.assign(default_map, data.default_map);
        }
        if (data.invited_map) {
            for (const key in invited_map)
                delete invited_map[key];
            Object.assign(invited_map, data.invited_map);
        }
        if (data.invited_inverted_map) {
            for (const key in invited_inverted_map)
                delete invited_inverted_map[key];
            Object.assign(invited_inverted_map, data.invited_inverted_map);
        }
    });
}
function saveKeyMaps() {
    const data = {
        default_map: default_map,
        invited_map: invited_map,
        invited_inverted_map: invited_inverted_map,
    };
    fetch("/accounts/keymap/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(data)
    })
        .then(async (response) => {
        const text = await response.text();
        try {
            const json = JSON.parse(text);
            getKeyMaps();
        }
        catch (e) {
            console.error("Invalid JSON returned by server:", e);
        }
    })
        .catch(error => {
        console.error("Error saving key maps:", error);
    });
}
// load player history
export function loadPlayerHistory(user) {
    const history_container = document.getElementById("history_games");
    if (history_container === null) {
        console.error("History container not found");
        return;
    }
    history_container.innerHTML = "";
    fetch("/getusersessions/?user=" + user)
        .then(response => response.json())
        .then(data => {
        // console.log("Player history data received:", data);
        for (let i = 0; i < data.length; i++) {
            let game = data[i];
            if (game === undefined || game === null)
                continue;
            let container_game = document.createElement('div');
            container_game.classList.add("container-fluid", "d-flex", "justify-content-center", "border", "border-light", "rounded-3", "mt-3");
            history_container.appendChild(container_game);
            let container_player_1 = document.createElement('div');
            container_player_1.classList.add("container", "d-flex", "flex-column", "justify-content-center", "text-light", "p-3");
            container_game.appendChild(container_player_1);
            let game_container_info = document.createElement('div');
            game_container_info.classList.add("container", "d-flex", "flex-column", "text-light", "p-3");
            container_game.appendChild(game_container_info);
            let EndAt = document.createElement('span');
            EndAt.classList.add("text-info", "fs-8", "align-self-center", "mx-3");
            EndAt.innerHTML = "EndAt: " + formatDate(game.ended_at);
            game_container_info.appendChild(EndAt);
            let vsText = document.createElement('span');
            vsText.innerHTML = "VS";
            vsText.classList.add("text-light", "fs-3", "align-self-center", "mx-3");
            game_container_info.appendChild(vsText);
            let Winner = document.createElement('span');
            Winner.classList.add("text-warning", "fs-6", "align-self-center", "mx-3");
            if (game.winner === null || game.winner === undefined)
                game.winner = "AI";
            Winner.innerHTML = "Winner: " + game.winner;
            game_container_info.appendChild(Winner);
            let container_player_2 = document.createElement('div');
            container_player_2.classList.add("container", "d-flex", "flex-column", "justify-content-center", "text-light", "p-3");
            container_game.appendChild(container_player_2);
            let player_1 = document.createElement('h6');
            player_1.innerHTML = game.player1;
            player_1.classList.add("text-success", "fs-5");
            container_player_1.appendChild(player_1);
            let player1_score = document.createElement('h6');
            player1_score.innerHTML = game.player1_score + " pts";
            player1_score.classList.add("text-success", "fs-6");
            container_player_1.appendChild(player1_score);
            let player_2 = document.createElement('h6');
            player_2.classList.add("text-danger", "fs-5");
            if (game.is_multiplayer === false)
                player_2.innerHTML = "AI";
            else
                player_2.innerHTML = game.player2;
            container_player_2.appendChild(player_2);
            let player2_score = document.createElement('h6');
            player2_score.innerHTML = game.player2_score + " pts";
            player2_score.classList.add("text-danger", "fs-6");
            container_player_2.appendChild(player2_score);
        }
    });
}
// load player statistics
export function loadPlayerStatistics(user) {
    fetch("/getuserstats/?user=" + user)
        .then(response => response.json())
        .then(data => {
        player_statistics.total_games_played = data.total_games_played || 0;
        player_statistics.total_games_wons = data.total_games_won || 0;
        player_statistics.total_points_scored = data.total_points_scored || 0;
        player_statistics.total_points_conceded = data.total_points_conceded || 0;
        player_statistics.total_tournaments_played = data.total_tournaments_played || 0;
        player_statistics.total_tournaments_won = data.total_tournaments_won || 0;
        const total_games_played = document.getElementById("total_games_played");
        const total_games_wons = document.getElementById("total_games_won");
        const total_points_scored = document.getElementById("total_points_scored");
        const total_points_conceded = document.getElementById("total_points_conceded");
        const total_tournaments_played = document.getElementById("total_tournaments_played");
        const total_tournaments_won = document.getElementById("total_tournaments_won");
        total_games_played.innerHTML = player_statistics.total_games_played.toString();
        total_games_wons.innerHTML = player_statistics.total_games_wons.toString();
        total_points_scored.innerHTML = player_statistics.total_points_scored.toString();
        total_points_conceded.innerHTML = player_statistics.total_points_conceded.toString();
        total_tournaments_played.innerHTML = player_statistics.total_tournaments_played.toString();
        total_tournaments_won.innerHTML = player_statistics.total_tournaments_won.toString();
    });
}
(async () => {
    await User.setUser();
    initUserInfo();
    initChatRoom();
    getKeyMaps();
    loadPlayerStatistics(User.get());
    loadPlayerHistory(User.get());
})();
// KEYBOARD SETTINGS PART
let toucheActive = null;
let KeyinnerText = "";
function loadKeyButtons() {
    const container_all_keys = document.getElementById("keys_container");
    container_all_keys.innerHTML = ""; // Clear previous buttons
    for (const key in default_map) {
        if (default_map[key]?.[1] == "noaction")
            continue;
        if (key == key.toUpperCase())
            continue
        // add element text
        let container_key = document.createElement('div');
        container_key.classList.add("w-50", "p-3", "text-center");
        container_all_keys.appendChild(container_key);
        let action_text = document.createElement('span');
        action_text.classList.add("text-light", "fs-6", "me-1");
        action_text.textContent = default_map[key]?.[0];
        container_key.appendChild(action_text);
        let button = document.createElement('button');
        button.classList.add("btn", "btn-outline-primary");
        button.id = key;
        button.textContent = key;
        button.addEventListener("click", () => {
            KeyinnerText = button.textContent || "";
            if (isLetter(KeyinnerText))
                KeyinnerText = KeyinnerText.toLowerCase()
            toucheActive = key;
            // console.log("Touche active:", toucheActive, KeyinnerText);
            button.textContent = "Appuyez sur une touche...";
        });
        container_key.appendChild(button);
    }
}

function isLetter(str) {
    return str.length === 1 && str.match(/[a-zA-Z]/i);
}

document.addEventListener("keydown", (event) => {
    if (toucheActive) {
        const touche = event.key
        const upperTouche = event.key
        if (isLetter(event.key))
        {
            const touche = event.key.toLowerCase();
            const upperTouche = event.key.toUpperCase();
        }
        const KeyActive = document.getElementById(toucheActive);
        // save to default_map
        if (!(touche in default_map)) {
            if (default_map[KeyinnerText]) {
                const actions = default_map[KeyinnerText];
                delete default_map[KeyinnerText];
                default_map[touche] = actions;
            }

            if (isLetter(KeyinnerText))
            {
                if (default_map[KeyinnerText.toUpperCase()]) {
                    const upactions = default_map[KeyinnerText.toUpperCase()]
                    delete default_map[KeyinnerText.toUpperCase()];    
                    default_map[upperTouche] = upactions;
                }
            }
            // save to invited_map
            if (invited_map[KeyinnerText]) {
                const actions = invited_map[KeyinnerText];
                delete invited_map[KeyinnerText];
                invited_map[touche] = actions;
            }

            if (isLetter(KeyinnerText))
            {
             if (invited_map[KeyinnerText.toUpperCase()]) {
                const upactions = invited_map[KeyinnerText.toUpperCase()]
                delete invited_map[KeyinnerText.toUpperCase()];    
                invited_map[upperTouche] = upactions;
            }
        }
            // save to invited_inverted_map
            if (invited_inverted_map[KeyinnerText]) {
                const actions = invited_inverted_map[KeyinnerText];
                delete invited_inverted_map[KeyinnerText];
                invited_inverted_map[touche] = actions;
            }

            if (isLetter(KeyinnerText))
            {

             if (invited_inverted_map[KeyinnerText.toUpperCase()]) {
                const upactions = invited_inverted_map[KeyinnerText.toUpperCase()]
                delete invited_inverted_map[KeyinnerText.toUpperCase()];    
                invited_inverted_map[upperTouche] = upactions;
            }
        }
    }
        console.log("default: ", default_map)
        console.log("invited: ", invited_map)
        console.log("inverted: ", invited_inverted_map)

        KeyActive.textContent = touche;
        toucheActive = null;
        saveKeyMaps();
    }
});
