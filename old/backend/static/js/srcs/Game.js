import { Scene } from "./Scene.js";

export class Game
{
    run = false;
    ctx;
    player1;
    player2;
    ball;
    p1_score = 0;
    p2_score = 0;

    constructor(ball, player1, player2, ctx)
    {
        this.ball = ball;
        this.player1 = player1;
        this.player2 = player2;
        this.ctx = ctx;
        this.stage = new Scene(this.ctx);
        this.drawScores();
        this.update('{"reset":true}');
    }

    stop()
    {
        if (this.run == true)
            this.run = false
    }

    go()
    {
        if (this.run == false)
            this.run = true
    }
    
    toogle()
    {
        this.run = !this.run
    }


    clearScene()
    {
        this.ctx.beginPath();
        this.ctx.fillStyle="#000000"
        this.ctx.fillRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
        this.ctx.fill();
    }

    drawScores()
    {
        let fontSize = 180
        this.ctx.font = `${fontSize}px "Press Start 2P", monospace`
        this.ctx.fillStyle="#494066"
        this.ctx.fillText(this.p1_score, (this.ctx.canvas.width / 2) - fontSize * 1.5, fontSize)
        this.ctx.fillText(this.p2_score, (this.ctx.canvas.width / 2) + fontSize, fontSize)
    }

    update(pos)
    {
        pos = JSON.parse(pos);
        let point = 0;
        this.clearScene();
        this.drawScores()
        let keys = (Object.keys(pos))
        keys.forEach(key => {
            if (key == "yp1")
                this.player1.update(pos.yp1)
            if (key == "yp2")
                this.player2.update(pos.yp2)    
        });
        this.stage.drawlevel(pos);
        point = this.ball.update(this.stage, this.player1, this.player2);
        if (point == 1)
        {
            this.p1_score++;
            this.ball.init()
        }
        if (point == 2)
        {
            this.p2_score++;
            this.ball.init()
        }
        point = 0
    }

}