export const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
function default_logger(msg) {
    // console.log(msg.message)
}
export function initSocket(endpoint, handle = default_logger) {
    const sock = new WebSocket(wsProtocol + '//' + window.location.host + endpoint, []);
    sock.onerror = function (error) {
        console.error('Erreur WebSocket:', error);
    };
    sock.onopen = () => console.log("✅ Connected on websocket", endpoint, " !!!!");
    sock.onmessage = (msg) => {
        let data = JSON.parse(msg.data);
        handle(data);
    };
    return sock;
}
