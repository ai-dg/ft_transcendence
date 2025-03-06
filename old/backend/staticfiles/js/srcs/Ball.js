export class Ball
{
    x;
    y;
    X_dir;
    Y_dir;
    oldX = 0;
    oldY = 0;
    r = 7;
    ctx;
    speed = 5;

    constructor(ctx)
    {  
        this.ctx = ctx;
        this.init()
        this.draw()
    }

    init()
    {
        console.log(this.ctx)
        this.x = this.ctx.canvas.width / 2;
        this.y = this.ctx.canvas.height / 2;
        this.angle = Math.random() * 2 * Math.PI;
        this.X_dir = this.speed * Math.cos(this.angle);
        this.Y_dir = this.speed * Math.sin(this.angle);
        this.speed++;
        console.log("xdir : ", this.X_dir, "- ydir : ", this.Y_dir, "- angle : ", this.angle)
    }
    

    draw()
    {
        this.ctx.beginPath();
        this.ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2, true);
        this.ctx.fillStyle="#FFFFFF"
        this.ctx.fill();
    }

    checkCollision(player1, player2)
    {
        if (this.y >= player1.startY() && this.y < player1.endY() && this.leftEdge() <= player1.endX() )
        {
            this.updateX()
  
            return true
        }
        if (this.y >= player2.startY() && this.y < player2.endY() && this.rightEdge() >= player2.startX())
        {
            this.updateX()
  
            return true
        }
        return false

    }

    updateX()
    {
        this.X_dir *= -1;
    }

    leftEdge(){
        return this.x - this.r;
    }
    rightEdge()
    {
        return this.x +  this.r;
    }

    updateY()
    {
        this.Y_dir *= -1;
    }

    update(stage, player1, player2)
    {
        this.oldY = this.y;
        this.oldX = this.x;
        let limits = stage.getBorders() 

        if (!this.checkCollision(player1, player2))
        {
            if (this.x + this.X_dir > this.ctx.canvas.width)
                return 1
            if (this.x + this.X_dir < 0)
                return 2
        }    
        if (this.y + this.Y_dir > limits.bottom - this.r)
            this.updateY()
        if (this.y + this.Y_dir < limits.top + this.r - 1)
            this.updateY()
        this.y = this.y + this.Y_dir;
        this.x = this.x + this.X_dir;
        this.draw();

    }

}