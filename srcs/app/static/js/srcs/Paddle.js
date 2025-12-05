export class Paddle {
    x;
    y;
    width;
    height;
    constructor(data, isAI = false) {
        const source = isAI ? data.player2 : data.player;
        this.x = source.x;
        this.y = source.y;
        this.width = source.width;
        this.height = source.height;
    }
    draw(ctx) {
        if (!ctx)
            return;
        ctx.fillStyle = "white";
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}
