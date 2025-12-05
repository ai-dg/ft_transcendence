import { game_scene } from "./Scene.js";
import { Ball } from "./Ball.js";
import { Paddle } from "./Paddle.js";
import { Score } from "./Score.js";
import { Numbers } from "./Numbers.js";
export const DEFAULT_GAME_PARAMS = { opponent: "remote", player: 2, max_pts: 10, win_condition: 5, level: "none" };
export let CUSTOM_GAME_PARAMS = { opponent: "remote", player: 2, max_pts: 10, win_condition: 5, level: "none" };
export class Game {
    data;
    scene;
    player;
    player2;
    ball;
    score;
    numbers;
    running;
    animationFrameId = null;
    constructor(data) {
        // console.log("🟢 Game class created");
        this.data = data;
        this.scene = game_scene;
        this.player = new Paddle(this.data, false);
        this.player2 = new Paddle(this.data, true);
        this.ball = new Ball(this.data);
        this.score = new Score(this.data.score);
        this.numbers = new Numbers(this.data.score);
        this.running = true;
        this.loop();
    }
    loop() {
        if (this.running) {
            this.render();
        }
        this.animationFrameId = requestAnimationFrame(() => this.loop());
    }
    start() {
        this.running = true;
    }
    stop() {
        this.running = false;
        this.scene.clear();
        this.numbers.clear();
    }
    render() {
        this.scene.clear();
        this.score.clear();
        this.numbers.clear();
        this.scene.draw([this.player, this.player2, this.ball]);
        this.score.draw([this.numbers]);
    }
    updateGame(newData) {
        this.data = newData;
        this.player.x = newData.player.x;
        this.player.y = newData.player.y;
        this.player2.x = newData.player2.x;
        this.player2.y = newData.player2.y;
        this.ball.update(newData);
        this.numbers.update(newData.score);
    }
}
