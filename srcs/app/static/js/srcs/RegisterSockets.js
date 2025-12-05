import { initSocket } from "./Sockets.js";
import { chat_handler } from "./Chat.js";
export const chat_socket = initSocket('/ws/chat/', chat_handler);
// export const pong_socket: WebSocket = initSocket('/ws/pong/')
// // ****** Initializing the test WebSocket
// export const socket_test: WebSocket = initSocket('/ws/')
// ****** Initializing the WebSocket with the game server
export const socket_game = initSocket('/ws/game/');
