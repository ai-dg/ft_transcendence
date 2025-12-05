export class Numbers {
    leftScore;
    rightScore;
    left_player;
    right_player;
    canvas;
    ctx;
    constructor(scoreData) {
        this.leftScore = scoreData.left || 0;
        this.rightScore = scoreData.right || 0;
        this.right_player = scoreData.right_player || "";
        if (scoreData.left_pseudo)
            this.left_player = scoreData.left_pseudo;
        else
            this.left_player = scoreData.left_player || "";
        if (scoreData.right_pseudo)
            this.right_player = scoreData.right_pseudo;
        else
            this.right_player = scoreData.right_player || "";
        this.canvas = document.getElementById(scoreData.canvas_id);
        if (!this.canvas) {
            console.error(`❌ ERREUR : Canvas avec ID '${scoreData.canvas_id}' introuvable.`);
            this.ctx = null;
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
        if (!this.ctx || !this.canvas)
            return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    draw() {
        if (!this.ctx || !this.canvas)
            return;
        this.ctx.fillStyle = "white";
        this.ctx.font = "35px Arial";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "middle";
        this.ctx.fillText(this.left_player.toString(), this.canvas.width / 4, this.canvas.height / 3.5);
        this.ctx.fillText(this.leftScore.toString(), this.canvas.width / 4, this.canvas.height / 1.5);
        this.ctx.fillText(this.right_player.toString(), (this.canvas.width * 3) / 4, this.canvas.height / 3.5);
        this.ctx.fillText(this.rightScore.toString(), (this.canvas.width * 3) / 4, this.canvas.height / 1.5);
        const scoreTextElement = document.getElementById("scoreText");
        if (scoreTextElement) {
            scoreTextElement.innerText = `${this.leftScore} - ${this.rightScore}`;
        }
    }
}
