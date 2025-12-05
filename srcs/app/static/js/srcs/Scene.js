export class Scene {
    canvas;
    ctx;
    constructor(data) {
        this.canvas = document.getElementById(data.scene.canvas_id);
        if (!this.canvas) {
            console.error(`❌ ERROR: Canvas with ID '${data.scene.canvas_id}' not found.`);
            this.ctx = null;
            return;
        }
        if (data.scene.width && data.scene.height) {
            this.canvas.width = data.scene.width;
            this.canvas.height = data.scene.height;
            this.canvas.style.width = `${this.canvas.width}px`;
            this.canvas.style.height = `${this.canvas.height}px`;
        }
        else {
            console.warn("⚠️ No canvas size defined, using default values.");
            this.canvas.width = 800;
            this.canvas.height = 400;
            this.canvas.style.width = "800px";
            this.canvas.style.height = "400px";
        }
        this.ctx = this.canvas.getContext("2d");
        if (!this.ctx) {
            console.error("❌ ERROR: Unable to get 2D context.");
            return;
        }
        console.log("✅ Canvas initialized:", this.canvas.width, "x", this.canvas.height);
    }
    getContext() {
        if (!this.ctx) {
            throw new Error("❌ ERROR: Unable to get 2D context.");
        }
        return this.ctx;
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
export let game_scene = new Scene({ scene: { canvas_id: "gameCanvas", width: 800, height: 400 } });
export let score_scene = new Scene({ scene: { canvas_id: "scoreCanvas", width: 400, height: 150 } });
