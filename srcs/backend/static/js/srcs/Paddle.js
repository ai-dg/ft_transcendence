export class Paddle {
    constructor(data, isAI = false) {
        const source = isAI ? data.ai : data.player;
        this.x = source.x;
        this.y = source.y;
        this.width = source.width;
        this.height = source.height;
    }

    draw(ctx) {
        if (!ctx) return;
        ctx.fillStyle = "white";
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}
