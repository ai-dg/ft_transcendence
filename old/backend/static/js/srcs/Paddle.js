export class Paddle{

    x = 0;
    y = 0;
    ctx;

    constructor(x,y, ctx)
    {
        this.x = x;
        this.y = y;
        this.ctx = ctx;
        this.paddleSize = 85
        this.paddleWidth = 10
        this.draw()
    }

    draw()
    {
       // console.log("draw called")
        this.ctx.beginPath();
        this.ctx.fillStyle="#FFFFFF";
        this.ctx.fillRect(this.x, this.y, this.paddleWidth, this.paddleSize);
        this.ctx.fill();
    }


    startY()
    {
        return this.y;
    }

    startX()
    {
        return this.x;
    }



    endY()
    {
        return this.y + this.paddleSize
    }


    endX()
    {
        return this.x + this.paddleWidth;
    }

    update(dir)
    {
        this.oldX = this.x
        this.oldY = this.y 
        if (dir > 0 && this.y + 10 < this.ctx.canvas.height - this.paddleSize - 20 )
            this.y += 10
        else if (dir < 0 &&  this.y -10 - 20 > 0)
            this.y -= 10
        this.draw();

    }
}