export class Ball {
    x;
    y;
    size;
    constructor(data) {
        this.x = data.ball.x;
        this.y = data.ball.y;
        this.size = data.ball.size;
    }
    update(newData) {
        this.x = newData.ball.x;
        this.y = newData.ball.y;
    }
    draw(ctx) {
        if (!ctx)
            return;
        ctx.fillStyle = "white";
        ctx.beginPath();
        ctx.arc(this.x + this.size / 2, this.y + this.size / 2, this.size / 2, 0, Math.PI * 2);
        ctx.fill();
    }
}
