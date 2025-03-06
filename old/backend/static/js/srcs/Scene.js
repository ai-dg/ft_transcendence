export class Scene{
    
    constructor(ctx)
    {
        this.ctx = ctx;

    }

    middleLine()
    {
        let startX, endX, startY;
        let length = 75;
        let color = "#555555";
        let off = 30;
        startX = Math.floor(this.ctx.canvas.width / 2) - 5
        endX = Math.floor(this.ctx.canvas.width / 2) + 5
        startY = 50
        while ( startY + length + 20 < this.ctx.canvas.height )
        {
          this.ctx.fillStyle = color;
          this.ctx.fillRect(startX, startY, 10, 70)
          startY = startY + length + off
          this.ctx.fill();
        }
    }

    topBar()
    {
        this.ctx.fillStyle = "white";
        this.ctx.fillRect(0, 10, this.ctx.canvas.width, 10)
        this.ctx.fill();
    }

    bottomBar()
    {
        this.ctx.fillStyle = "white";
        this.ctx.fillRect(0, this.ctx.canvas.height - 20 , this.ctx.canvas.width, 10)
        this.ctx.fill();
    }

    drawlevel(pos)
    {
        this.middleLine()
        this.topBar()
        this.bottomBar()
    }

    getBorders()
    {
        return {top: 20, bottom: this.ctx.canvas.height - 20}
    }
}