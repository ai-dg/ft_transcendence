import { Numbers } from "./Numbers.js";
import { game_scene, score_scene } from "./Scene.js";
let current_timeout = null;
export function cancel_timeout() {
    if (current_timeout)
        clearTimeout(current_timeout);
    current_timeout = null;
}
export function wait_and_clear(time) {
    current_timeout = setTimeout(clear_all_canvas, time);
}
export function display_game_message(message) {
    // console.log("game create message called")
    game_scene.clear();
    cancel_timeout();
    let canvas = document.getElementById("gameCanvas");
    let ctx = game_scene.getContext();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "20px Arial";
    ctx.fillStyle = "white";
    ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}
export function display_game_count(message, conf = false) {
    game_scene.clear();
    cancel_timeout();
    let canvas = document.getElementById("gameCanvas");
    let ctx = game_scene.getContext();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "80px Arial";
    ctx.fillStyle = "white";
    ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}
function get_game_stats(stats) {
    const games = stats.games;
    const players = stats.players;
    let map = new Map();
    players.forEach((player) => {
        map.set(player, { wins: 0, score: 0, pseudo: null });
    });
    games.forEach((game) => {
        let winner = map.get(game.winner);
        winner.wins += 1;
        const player1 = map.get(game.player1.name);
        player1.pseudo = game.player1.pseudo;
        player1.score += game.player1.score;
        const player2 = map.get(game.player2.name);
        player2.pseudo = game.player2.pseudo;
        player2.score += game.player2.score;
    });
    const playersArray = [...map.entries()];
    let rank = playersArray.sort((playerA, playerB) => {
        const [nameA, statsA] = playerA;
        const [nameB, statsB] = playerB;
        if (statsB.wins !== statsA.wins) {
            return statsB.wins - statsA.wins;
        }
        if (statsB.score !== statsA.score) {
            return statsB.score - statsA.score;
        }
        return nameA.localeCompare(nameB);
    });
    return rank.map(([name, stats]) => stats.pseudo ?? name);
}
export function display_game_stats(stats) {
    game_scene.clear();
    score_scene.clear();
    cancel_timeout();
    const rank = get_game_stats(stats);
    let canvas = document.getElementById("gameCanvas");
    let ctx = game_scene.getContext();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "20px Arial";
    ctx.fillStyle = "white";
    let y = 150;
    let pos = 1;
    ctx.fillText('Rank :', canvas.width / 2, 100);
    rank.forEach((name) => {
        ctx.fillText(`${pos} - ${name}`, canvas.width / 2, y);
        y += 50;
        pos += 1;
    });
}
export function clear_all_canvas() {
    game_scene.clear();
    score_scene.clear();
    display_game_message("Please Join or Create a game or Tournament");
}
export function display_game_score(data) {
    cancel_timeout();
    console.log(data);
    let param;
    if (data.status == "init") {
        param = data.score;
    }
    else {
        let player1 = data.player1;
        let player2 = data.player2;
        let p1score = player1.score;
        let p2score = player2.score;
        if (player1.side == "left")
            param = {
                left: p1score,
                left_player: player1.name,
                left_pseudo: player1.pseudo,
                right: p2score,
                right_player: player2.name,
                right_pseudo: player2.pseudo,
                canvas_id: "scoreCanvas"
            };
        else
            param = {
                left: p2score,
                left_player: player2.name,
                left_pseudo: player2.pseudo,
                right: p1score,
                right_player: player1.name,
                right_pseudo: player1.pseudo,
                canvas_id: "scoreCanvas"
            };
    }
    let scores = new Numbers(param);
    scores.draw();
    // if (data.status != 'init')
    //     wait_and_clear(20000)
}
