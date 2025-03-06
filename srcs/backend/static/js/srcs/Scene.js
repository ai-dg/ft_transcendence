export class Scene {
    constructor(data) {
        this.canvas = document.getElementById(data.scene.canvas_id);
        
        if (!this.canvas) {
            console.error(`❌ ERROR: Canvas with ID '${data.scene.canvas_id}' not found.`);
            return;
        }
        
        if (data.scene.width && data.scene.height) {
            this.canvas.width = data.scene.width;
            this.canvas.height = data.scene.height;

            this.canvas.style.width = `${this.canvas.width}px`;
            this.canvas.style.height = `${this.canvas.height}px`;
        } else {
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

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    draw(objects) {
        objects.forEach(obj => obj.draw(this.ctx));
    }
}
