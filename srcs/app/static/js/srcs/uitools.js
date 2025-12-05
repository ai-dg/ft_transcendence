export function getElements(classname) {
    return Array.from(document.getElementsByClassName(classname));
}
export function close_windows() {
    let wins = getElements("closer");
    wins.forEach((win) => {
        win.classList.add("d-none");
    });
}
export function notification_message(message, from = null) {
    document.body.insertAdjacentHTML('beforeend', `<alert-box
        alert-msg="${message}"
        notify="true"
        class="alert-box">`);
}
export function getRandomRGBAColor() {
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    const a = Math.random().toFixed(2);
    return `rgba(${r}, ${g}, ${b}, ${a})`;
}
export function color_canvas() {
    const score = document.getElementById("scoreCanvas");
    const scene = document.getElementById("gameCanvas");
    const alert_msg = document.querySelector(".game-alert");
    let style = `solid ${getRandomRGBAColor()}`;
    scene.style.border = `3px ${style}`;
    score.style.border = `3px ${style}`;
    alert_msg.style.border = `1px ${style}`;
}
export const PILLS = Object.freeze({
    GAMES: "isgame",
    TOURNAMENTS: "istournament",
    ALLGAMES: "allgames",
    MESSAGES: "ismessage"
});
export function show_pill(pill_id, nb) {
    const el = document.getElementById(pill_id);
    if (!el)
        return;
    el.classList.remove("d-none");
    el.textContent = `${nb}`;
}
export function hide_pill(pill_id) {
    const el = document.getElementById(pill_id);
    if (!el)
        return;
    el.classList.add("d-none");
    el.textContent = "";
}
export function count_child_nodes(el) {
    let nodes = null;
    if (!el)
        return 0;
    nodes = Array.from(el.children);
    return nodes.length;
}
