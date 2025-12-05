export const locale = navigator.language || "fr-FR";
export function formatDate(date) {
    let d = new Date(date);
    let d_date = d.toLocaleDateString(locale);
    let d_hour = d.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
    if (d_date === today())
        return d_hour;
    else
        return `${d_date} ${d_hour}`;
}
export function today() {
    let date = new Date();
    return date.toLocaleDateString(locale);
}
export function extractHour(date) {
    let index = date.indexOf(" ");
    if (index > 0)
        return date.slice(index);
    return date;
}
