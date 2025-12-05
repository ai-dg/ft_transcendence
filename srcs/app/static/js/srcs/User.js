import { getUrl } from "./Urls.js";
import { moveElement, MouseMove, selectImage, getAvatarFromUser } from "./Avatars.js";
import { chat_socket } from "./RegisterSockets.js";
export class User {
    static #rooms = {};
    static #user;
    static #banned_user = [];
    static #users = [];
    static #set(data) {
        User.#rooms[data.room_id] = data.sender;
    }
    static setConnectedUsers(data) {
        User.#users = data;
    }
    static getConnectedUsers() {
        return User.#users;
    }
    static same(data) {
        if (data.sender === User.#rooms[data.room_id])
            return true;
        User.#set(data);
        return false;
    }
    static async setUser() {
        try {
            let res = await fetch(getUrl("getuser/"), { method: 'GET', credentials: 'include' });
            let data = await res.json();
            User.#user = data.username;
        }
        catch (err) {
            console.error('User not authenticated');
        }
    }
    static async setBanned(banned) {
        User.#banned_user = [];
        banned.forEach((element) => {
            User.#banned_user.push(element.username);
        });
    }
    static getBanned() {
        return User.#banned_user;
    }
    static get() {
        return User.#user;
    }
}
export async function get_user() {
    try {
        let url = getUrl("getuser/");
        const response = await fetch(getUrl("getuser/"), { method: 'GET', credentials: 'include' });
        if (!response.ok)
            throw new Error('User not authenticated');
        const data = await response.json();
        return data.username;
    }
    catch (err) {
        console.error(err);
        return null;
    }
}
export function initUserInfo() {
    const load_avatar = document.getElementById("avatar");
    const userDetailsWrapper = document.getElementById("userDetailsWrapper");
    const change_avatar_btn = document.querySelector('#change-avatar-btn');
    const avatar_preview = document.querySelector(".avatar-preview");
    getAvatarFromUser(User.get(), avatar_preview, { height: 128, width: 128, size: null });
    change_avatar_btn.addEventListener("click", (e) => {
        userDetailsWrapper.classList.add("d-none");
        const old_avatar_image = document.getElementById('avatar_image');
        if (old_avatar_image)
            old_avatar_image.classList.add("d-none");
    });
    load_avatar.addEventListener("change", (event) => {
        const avatarCropWrapper = document.getElementById("avatarCropWrapper");
        let image = document.querySelector(".avatar-view");
        avatarCropWrapper.classList.remove("d-none");
        if (load_avatar.files && load_avatar.files.length > 0) {
            let imageUrl = URL.createObjectURL(load_avatar.files[0]);
            let element = new Image();
            element.src = imageUrl;
            element.id = "loadedimage";
            element.onload = () => {
                let img_width = element.naturalWidth;
                let img_height = element.naturalHeight;
                if (img_height > img_width) {
                    let height = avatarCropWrapper.offsetHeight * 90 / 100;
                    element.style.height = `${height}px`;
                    element.style.width = "auto";
                }
                else {
                    let width = avatarCropWrapper.offsetWidth * 90 / 100;
                    element.style.height = "auto";
                    element.style.width = `${width}px`;
                }
                image.innerHTML = "";
                image.appendChild(element);
                const crop_box = document.createElement("canvas");
                crop_box.id = "crop_box";
                crop_box.width = 128;
                crop_box.height = 128;
                image.appendChild(crop_box);
                const initialRect = crop_box.getBoundingClientRect();
                MouseMove.setDistance({ x: 0, y: 0 });
                moveElement({
                    clientX: initialRect.left,
                    clientY: initialRect.top
                });
                crop_box.addEventListener("mousedown", (mdevent) => {
                    let rect = crop_box.getBoundingClientRect();
                    let offsetX = mdevent.clientX - rect.left;
                    let offsetY = mdevent.clientY - rect.top;
                    MouseMove.setDistance({ x: offsetX, y: offsetY });
                    document.addEventListener("mousemove", moveElement);
                });
                document.addEventListener("mouseup", (muevent) => {
                    document.removeEventListener("mousemove", moveElement);
                });
                document.addEventListener("mouseleave", (muevent) => {
                    document.removeEventListener("mousemove", moveElement);
                });
                const crop_btn = document.getElementById("crop-button");
                crop_btn.addEventListener("click", function (e) {
                    selectImage(e);
                    avatarCropWrapper.classList.add("d-none");
                    userDetailsWrapper.classList.remove("d-none");
                });
                URL.revokeObjectURL(imageUrl);
            };
        }
        else
            console.log("fail choosing a file");
    });
}
export async function setRemoteAvatar(blob_image) {
    let formdata = new FormData();
    let url = getUrl("accounts/update/");
    formdata.append("avatar", blob_image, `${User.get()}_avatar.png`);
    let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
    try {
        let res = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            credentials: "include",
            body: formdata
        });
        if (!res.ok)
            return;
        let data = await res.json();
        chat_socket.send(JSON.stringify({ action: "account_update", user: User.get() }));
    }
    catch (err) {
        console.error(err);
    }
}
export async function updateUser() {
    let url = getUrl("accounts/update/");
    const pseudofield = document.getElementById("pseudo");
    const avatar_img = document.getElementById("avatar_image");
    let avatar = "default";
    let blob = null;
    let formdata = new FormData();
    if (pseudofield && pseudofield.value != "") {
        formdata.append("pseudo", pseudofield.value);
    }
    if (avatar_img) {
        blob = await (await fetch(avatar_img.src)).blob();
        if (blob)
            formdata.append("avatar", blob, `${User.get()}_avatar.png`);
    }
    let csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken
        },
        credentials: "include",
        body: formdata
    }).then(res => {
        res.json();
        chat_socket.send(JSON.stringify({ action: "account_update", user: User.get() }));
    })
        .catch(err => console.error(err));
}
