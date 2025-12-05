export class Score {
    canvas;
    ctx;
    constructor(scoreData) {
        this.canvas = document.getElementById(scoreData.canvas_id);
        if (!this.canvas) {
            console.error(`❌ ERROR: Canvas with ID '${scoreData.canvas_id}' not found.`);
            this.ctx = null;
            return;
        }
        this.canvas.width = scoreData.width || 200;
        this.canvas.height = scoreData.height || 100;
        this.canvas.style.width = `${this.canvas.width}px`;
        this.canvas.style.height = `${this.canvas.height}px`;
        this.ctx = this.canvas.getContext("2d");
        if (!this.ctx) {
            console.error("❌ ERROR: Unable to get 2D context.");
            return;
        }
        console.log("✅ Score canvas initialized:", this.canvas.width, "x", this.canvas.height);
    }
    clear() {
        if (!this.ctx || !this.canvas)
            return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    draw(objects) {
        if (!this.ctx)
            return;
        objects.forEach(obj => obj.draw(this.ctx));
    }
}
