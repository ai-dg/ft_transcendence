export function getUrl(endpoint) {
    if (endpoint[0] != '/')
        endpoint = '/' + endpoint;
    return window.location.protocol + '//' + window.location.host + endpoint;
}
