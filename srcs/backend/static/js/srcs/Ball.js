export class Ball {
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
        if (!ctx) return;

        ctx.fillStyle = "white";
        ctx.fillRect(this.x, this.y, this.size, this.size);
    }
}
