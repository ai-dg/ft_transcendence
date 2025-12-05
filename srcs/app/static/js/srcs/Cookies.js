export function getCookieJSONValue(field) {
    let cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        if (!cookie.includes("="))
            continue;
        let parts = cookie.split("=");
        if (parts.length > 2)
            continue;
        let [key, value] = parts;
        if (key === field)
            return JSON.parse(decodeURIComponent(value));
    }
    return [];
}
export function setCookieJSONValue(field, value, filter = {}) {
    let values = getCookieJSONValue(field);
    if (typeof (values) === 'string')
        values = [values];
    if (!Array.isArray(values))
        values = [];
    if (!values.includes(value)) {
        values.unshift(value);
        if (typeof filter.length === "number" && filter.length > 0)
            if (values.length > filter.length)
                values.pop();
    }
    document.cookie = `${field}=${encodeURIComponent(JSON.stringify(values))}; samesite=strict; path=/; max-age=31536000`;
}
export function getCookieValue(field) {
    let cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        if (!cookie.includes("="))
            continue;
        let parts = cookie.split("=");
        if (parts.length > 2)
            continue;
        let [key, value] = parts;
        if (key === field)
            return decodeURIComponent(value);
    }
    return null;
}
export function setCookieValue(field, value) {
    document.cookie = `${field}=${encodeURIComponent(value)}; samesite=strict; path=/; max-age=31536000`;
}
