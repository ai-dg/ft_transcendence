// ****** Importing modules
import { Game } from "./srcs/Game.js";

let data_game = null;
window.gameInstance = null;
let lastUpdate = Date.now();
let isSocketReady = false; 

// ****** Initializing the test WebSocket
const protocol = (() => {
    if (window.location.protocol === "https:") {
        return "wss://";
    } else {
        return "ws://";
    }
})();

const host = (() => {
    if (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost") {
        return "127.0.0.1:8001";
    } else {
        return `${window.location.hostname}:16443`;
    }
})();

const socket_test = new WebSocket(`${protocol}${host}/ws/`);
socket_test.onopen = () => console.log("✅ Test WebSocket connected!");
socket_test.onmessage = (event) => console.log("📩 Message received:", event.data);
socket_test.onerror = (event) => console.log("❌ WebSocket error:", event);
socket_test.onclose = () => console.log("🔴 Test WebSocket disconnected!");

// ****** Initializing the WebSocket with the game server
const socket_game = new WebSocket(`${protocol}${host}/ws/game/`);

socket_game.onopen = () => {
    console.log("✅ [app.js] WebSocket (Game) connected!");
    isSocketReady = true;
};

socket_game.onmessage = (event) => {
    let now = Date.now();
    data_game = JSON.parse(event.data);
    console.log(`data ${event.data}`)

    lastUpdate = now;

    if (window.gameInstance) {
        window.gameInstance.updateGame(data_game);
    } else {
        console.log("🎮 Creating a new game instance!");
        window.gameInstance = new Game(data_game);
    }
};

socket_game.onerror = (event) => console.log("❌ [app.js] WebSocket error:", event);
socket_game.onclose = () => {
    console.log("🔴 [app.js] WebSocket disconnected!");
    isSocketReady = false;
};

// ****** Listening for DOMContentLoaded to ensure the canvas exists
document.addEventListener("DOMContentLoaded", () => {
    console.log("📌 DOM loaded, initializing the game...");

    // ****** Handling interface buttons
    let logoutButton = document.querySelector("#logout");
    if (logoutButton) {
        logoutButton.addEventListener("click", () => window.location.href = "/logout/");
    }

    let newGameButton = document.getElementById("new_game");
    let stopGameButton = document.getElementById("stop_game");
    let chatButton = document.getElementById("chat");
    let signupButton = document.getElementById("signup");
    let signinButton = document.getElementById("signin");

    if (signupButton) {
        signupButton.addEventListener("click", () => {
            console.log("✅ 'Sign Up' button clicked!");
            let chatbox = document.querySelector(".signupwrapper");
            if (!chatbox) {
                console.error("❌ ERROR: .signupwrapper not found!");
                return;
            }
            chatbox.style.display = chatbox.style.display === "block" ? "none" : "block";
        });
    } else {
        console.error("❌ ERROR: 'Sign Up' button not found!");
    }

    if (signinButton) {
        signinButton.addEventListener("click", () => {
            console.log("✅ 'Sign In' button clicked!");
            let chatbox = document.querySelector(".signinwrapper");
            if (!chatbox) {
                console.error("❌ ERROR: .signinwrapper not found!");
                return;
            }
            chatbox.style.display = chatbox.style.display === "block" ? "none" : "block";
        });
    } else {
        console.error("❌ ERROR: 'Sign In' button not found!");
    }

    if (chatButton) {
        chatButton.addEventListener("click", () => {
            let chatbox = document.querySelector(".chatwrapper");
            chatbox.style.display = chatbox.style.display === "block" ? "none" : "block";
        });
    }

    if (newGameButton) {
        newGameButton.addEventListener("click", () => {
            console.log("🟢 'New Game' button clicked, sending START command...");
            sendStartCommand();
        });
    }

    if (stopGameButton) {
        stopGameButton.addEventListener("click", () => {
            console.log("🟢 'Stop Game' button clicked, sending STOP command...");
            sendStopCommand();
        });
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowUp") {
        sendMoveCommand("move_up");
    } else if (event.key === "ArrowDown") {
        sendMoveCommand("move_down");
    }
});

document.addEventListener("keyup", (event) => {
    sendMoveCommand("stop");
});

function sendMoveCommand(action) {
    if (isSocketReady && socket_game.readyState === WebSocket.OPEN) {
        socket_game.send(JSON.stringify({ "action": action }));
    } else {
        console.warn("⚠️ WebSocket is not ready, retrying...");
        setTimeout(() => sendMoveCommand(action), 500);
    }
}

function sendStartCommand() {
    if (isSocketReady && socket_game.readyState === WebSocket.OPEN) {
        console.log("🚀 Sending START command to the server...");
        socket_game.send(JSON.stringify({ "command": "start" }));
    } else {
        console.warn("⚠️ WebSocket not ready, waiting...");
        setTimeout(sendStartCommand, 500);
    }
}

function sendStopCommand() {
    if (isSocketReady && socket_game.readyState === WebSocket.OPEN) {
        console.log("🚀 Sending STOP command to the server...");
        socket_game.send(JSON.stringify({ "command": "stop" }));
    } else {
        console.warn("⚠️ WebSocket is not ready yet, retrying...");
        setTimeout(sendStopCommand, 500);
    }
}
