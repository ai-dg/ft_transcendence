export function getCSRFToken() {
    const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
    return csrfToken;
}
