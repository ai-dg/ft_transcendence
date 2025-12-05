export let default_map = {
    q: ["move_up", "stop"],
    Q: ["move_up", "stop"],
    d: ["move_down", "stop"],
    D: ["move_down", "stop"],
    ArrowLeft: ["move_down", "stop"],
    ArrowRight: ["move_up", "stop"],
    p: ["pause_request", "noaction"],
    space: ["launch", "noaction"]
};
export let invited_map = {
    q: ["move_up", "stop"],
    Q: ["move_up", "stop"],
    d: ["move_down", "stop"],
    D: ["move_down", "stop"],
    ArrowLeft: ["move2_up", "stop2"],
    ArrowRight: ["move2_down", "stop2"],
    p: ["pause_request", "noaction"],
    space: ["launch", "noaction"]
};
export let invited_inverted_map = {
    q: ["move2_up", "stop2"],
    Q: ["move2_up", "stop2"],
    d: ["move2_down", "stop2"],
    D: ["move2_down", "stop2"],
    ArrowLeft: ["move_down", "stop"],
    ArrowRight: ["move_up", "stop"],
    p: ["pause_request", "noaction"],
    space: ["launch", "noaction"]
};
