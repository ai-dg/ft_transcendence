export class Numbers {
    constructor(scoreData) {  
        this.leftScore = scoreData.left || 0;
        this.rightScore = scoreData.right || 0;

        
        this.canvas = document.getElementById(scoreData.canvas_id);
        if (!this.canvas) {
            console.error(`❌ ERREUR : Canvas avec ID '${scoreData.canvas_id}' introuvable.`);
            return;
        }
        this.ctx = this.canvas.getContext("2d");
        if (!this.ctx) {
            console.error("❌ ERREUR : Impossible d'obtenir le contexte 2D.");
            return;
        }
    }

    update(scoreData) {
        this.leftScore = scoreData.left;
        this.rightScore = scoreData.right;
        this.clear();  
        this.draw();  
    }

    clear() {
        if (!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    draw() {
        if (!this.ctx) return;
        
        this.ctx.fillStyle = "white";
        this.ctx.font = "40px Arial";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "middle";

        this.ctx.fillText(this.leftScore, this.canvas.width / 4, this.canvas.height / 2);
        this.ctx.fillText(this.rightScore, (this.canvas.width * 3) / 4, this.canvas.height / 2);

        document.getElementById("scoreText").innerText = `${this.leftScore} - ${this.rightScore}`;
    }
}
