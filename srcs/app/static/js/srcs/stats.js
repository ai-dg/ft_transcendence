import { close_windows } from "../srcs/uitools.js";
import { loadPlayerStatistics, loadPlayerHistory } from "../app.js";
export function get_user_stats(event) {
    const el = event.target;
    const username = el.getAttribute("username");
    let target = document.getElementById("BestScoreWrapper");
    if (target.classList.contains("d-none")) {
        close_windows();
        (async () => {
            loadPlayerStatistics(username);
            loadPlayerHistory(username);
        })();
        target.classList.remove("d-none");
        let titlebestscore = document.getElementById("bestScoreTitle");
        titlebestscore.innerText = "Best Score of " + username;
    }
}
