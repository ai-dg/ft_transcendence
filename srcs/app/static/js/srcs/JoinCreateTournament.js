import { initSocket } from "./Sockets.js";
import { User } from "./User.js";
import { display_game_message, display_game_stats } from "./GameNotifications.js";
let tournament_socket_is_ready = false;
const active_tournaments = {};
export let tournament_socket_outside = null;
export async function play_tournament(params) {
    let tournaments_socket_id = null;
    if (active_tournaments[params.tournament_uid]) {
        tournaments_socket_id = active_tournaments[params.tournament_uid];
        tournament_socket_outside = tournaments_socket_id;
    }
    else {
        tournaments_socket_id = initSocket(`/ws/pong/tournament/${params.tournament_uid}`);
        tournaments_socket_id.onopen = () => {
            console.log("✅ Tournament WebSocket connected!");
            tournament_socket_is_ready = true;
        };
        tournaments_socket_id.onmessage = (event) => run_tournament(event, tournaments_socket_id);
        tournaments_socket_id.onerror = (event) => console.log("❌ WebSocket error:", event);
        tournaments_socket_id.onclose = () => {
            console.log("🔴 Tournament WebSocket disconnected!");
            tournament_socket_is_ready = false;
            delete active_tournaments[params.tournament_uid];
            tournament_socket_outside = null;
        };
    }
}
export function handle_tournament_end(data, tournaments_socket_id) {
    let user = User.get();
    if (data.status == "end_game" || data.status == "tournament_over") {
        if (window.game_instance) {
            window.game_instance.stop();
            window.game_instance = null;
        }
        if (data.status == "end_game") {
            let player1 = data.player1.name;
            let player2 = data.player2.name;
            if (data.winner === user && (data.winner === player1 || data.winner === player2))
                display_game_message("You win the game ! Please wait for your opponent");
            else if (data.winner != user && (user === player1 || user === player2))
                display_game_message(`Game Over, ${data.winner} win the game !`);
        }
        if (data.status == "tournament_over") {
            if (data.winner === user)
                display_game_message("You win the tournament !");
            else
                display_game_message(`Game Over, ${data.winner} win the tournament !`);
            setTimeout(() => {
                tournaments_socket_id.close(1000);
                display_game_stats(data.stats);
            }, 5000);
        }
    }
}
export function run_tournament(event, tournaments_socket_id) {
    const data = JSON.parse(event.data);
    // console.log("TOURNAMENT socket :");
    // console.log(data);
    // if (data.status)
    //     console.log("status", data.status)
    if (data.status == "end_game" || data.status == "tournament_over")
        handle_tournament_end(data, tournaments_socket_id);
}
