export class Fold extends HTMLElement {
    target = "";
    type = "";
    open = true;
    constructor() {
        super();
        this.classList.add("folders");
        this.type = this.getAttribute("type");
        this.target = this.getAttribute("target");
        const target = document.querySelector("." + this.target);
        if (this.open === true) { }
        else { }
        const el = document.createElement("i");
        this.appendChild(el);
        if (this.type === "fold") {
            this.classList.add("fold");
            el.classList.add("bi", "bi-chevron-up");
            this.open = false;
        }
        if (this.type === "unfold") {
            el.classList.add("bi", "bi-chevron-up");
            this.open = true;
        }
        this.addEventListener("click", () => {
            const target = document.querySelector("." + this.target);
            this.classList.toggle("fold");
            target.classList.toggle("window-hide");
            this.open = !this.open;
        });
    }
    static get observedAttributes() {
        return ['type', 'target'];
    }
    connectedCallback() {
    }
    disconnectedCallback() {
    }
    attributeChangedCallback(name, oldValue, newValue) {
        // console.log(`Attribute ${name} has changed.`);
    }
}
