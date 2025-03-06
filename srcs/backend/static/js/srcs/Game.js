import { Scene } from "./Scene.js";
import { Ball } from "./Ball.js";
import { Paddle } from "./Paddle.js";
import { Score } from "./Score.js";
import { Numbers } from "./Numbers.js";

export class Game {
    constructor(data) {
        console.log("🟢 Game class created");

        this.data = data;
        this.scene = new Scene(this.data);
        this.player = new Paddle(this.data, false);
        this.ai = new Paddle(this.data, true);
        this.ball = new Ball(this.data);
        this.score = new Score(this.data.score);  
        this.numbers = new Numbers(this.data.score);  
        
        this.loop();
    }

    loop() {
        this.render();
        requestAnimationFrame(() => this.loop());
    }

    render() {
        this.scene.clear();
        this.score.clear(); 
        this.numbers.clear(); 
        this.scene.draw([this.player, this.ai, this.ball]);
        this.score.draw([this.numbers]);
    }

    updateGame(newData) {
        this.data = newData;  
        this.player.x = newData.player.x;
        this.player.y = newData.player.y;
        this.ai.x = newData.ai.x;
        this.ai.y = newData.ai.y;

        this.ball.update(newData);
        this.numbers.update(newData.score);
    }
    
}
