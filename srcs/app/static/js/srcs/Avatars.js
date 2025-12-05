import { getCSRFToken } from "./Security.js";
import { getUrl } from "./Urls.js";
import { setRemoteAvatar, User } from "./User.js";
import { get_user_stats } from "./stats.js";
export const defaultAvatarBackgroundColors = [
    "#2C3E50", // Bleu minuit
    "#8E44AD", // Prune
    "#3B3B98", // Indigo foncé
    "#27AE60", // Vert sapin
    "#16A085", // Bleu pétrole
    "#1ABC9C", // Vert océan
    "#2980B9", // Bleu vif
    "#D35400", // Orange foncé
    "#C0392B", // Rouge grenat
    "#A93226", // Rouge brique
    "#E84393", // Rose foncé
    "#6C5CE7", // Violet électrique
    "#00B894", // Vert lime foncé
    "#0984E3", // Bleu glacier
    "#2C2C54", // Indigo profond
    "#1F618D", // Bleu ciel foncé
    "#6C3483", // Violet métallique
    "#34495E", // Bleu acier
    "#7B241C", // Brun cacao
    "#145A32", // Olive foncé
    "#273C75", // Bleu roi
    "#B03A2E", // Rouge carmin
    "#B9770E", // Jaune doré foncé
    "#196F3D", // Vert forêt sombre
    "#1A5276", // Bleu nuit
    "#512E5F", // Violet raisin
    "#2D3436", // Gris anthracite
    "#192A56", // Bleu marine
    "#30336B", // Ble
];
export const avatar_map = {};
export class MouseMove {
    static #offsetX = 0;
    static #offsetY = 0;
    static getDistance(newpos) {
        let distance = {
            x: MouseMove.#offsetX,
            y: MouseMove.#offsetY
        };
        return distance;
    }
    static setDistance(newpos) {
        MouseMove.#offsetX = newpos.x,
            MouseMove.#offsetY = newpos.y;
    }
}
export function moveElement(event) {
    let x = event.clientX; // position x de la souris
    let y = event.clientY; // position y de la souris
    let move = MouseMove.getDistance({ x: x, y: y }); // déplacement X et Y par rapport a la position précédente...
    let child = document.getElementById("crop_box");
    let imgctx = child.getContext("2d");
    let image = document.getElementById("loadedimage");
    let rect = image.getBoundingClientRect();
    let moveX = event.clientX - rect.left - move.x;
    let moveY = event.clientY - rect.top - move.y;
    moveX = Math.max(0, Math.min(moveX, rect.width - child.offsetWidth));
    moveY = Math.max(0, Math.min(moveY, rect.height - child.offsetHeight));
    // ratio entre l'image source et l'image affichée
    const scaleX = image.naturalWidth / rect.width;
    const scaleY = image.naturalHeight / rect.height;
    //coordonnées source en fonction du ratio
    const sourceX = moveX * scaleX;
    const sourceY = moveY * scaleY;
    const sourceWidth = child.width * scaleX;
    const sourceHeight = child.height * scaleY;
    imgctx.clearRect(0, 0, child.width, child.height);
    imgctx.drawImage(image, sourceX, // position x ajustée dans l'image source
    sourceY, // position y ajustée dans l'image source
    sourceWidth, // largeur ajustée à extraire
    sourceHeight, // hauteur ajustée à extraire
    0, // x destination (canvas)
    0, // y destination (canvas)
    child.width, // largeur dans le canvas
    child.height // hauteur dans le canvas
    );
    child.style.left = `${moveX}px`;
    child.style.top = `${moveY}px`;
}
export function selectImage(event) {
    const load_avatar = document.getElementById("avatar");
    const child = document.getElementById("crop_box");
    const image = document.querySelector(".avatar-view");
    const avatar_crop_wrapper = document.querySelector(".avatarCropWrapper");
    const crop_btn = document.querySelector("#crop-button");
    const change_avatar_btn = document.querySelector('#change-avatar-btn');
    let dataURL = child.toDataURL();
    const preview = document.querySelector(".avatar-preview");
    let imgElement = document.createElement("img");
    imgElement.src = dataURL;
    imgElement.id = "avatar_image";
    imgElement.style.width = "128px";
    imgElement.style.height = "128px";
    imgElement.classList.add("avatar-large");
    preview.innerHTML = "";
    preview.appendChild(imgElement);
    image.innerHTML = "";
    // load_avatar.style.display = "block";
    // load_avatar.classList.remove("d-none")
    // change_avatar_btn.classList.remove("d-none")
    // change_avatar_btn.style.display = "block";
    crop_btn.removeEventListener('click', selectImage);
    // avatar_wrapper.removeChild(crop_btn)
}
export async function loadAvatar(username, element, format) {
    const formdata = new FormData();
    formdata.append("username", username);
    fetch(getUrl("accounts/avatar/?username=" + username), {
        method: "GET",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        credentials: "include"
    }).then(async (res) => {
        if (!res.ok) {
            if (username === User.get()) {
                let blob = await setDefaultAvatar(username);
                return blob;
            }
            throw new Error('Avatar not found');
        }
        return res.blob();
    }).then(blob => {
        if (blob) {
            avatar_map[username] = blob;
            element.appendChild(getAvatar(blob, format, username));
        }
        else
            reloadAvatar(username);
    })
        .catch(err => {
        element.appendChild(getDefaultAvatar(username, format));
    });
}
export async function getAvatarFromUser(username, element, format = null) {
    if (!avatar_map[username])
        loadAvatar(username, element, format);
    else
        element.appendChild(getAvatar(avatar_map[username], format, username));
}
export function getAvatar(blob, format, username) {
    const avatar = document.createElement("div");
    avatar.classList.add("avatar");
    const img = document.createElement('img');
    img.classList.add("avatar_image");
    img.classList.add(`${username}_avatar`);
    img.setAttribute("username", username);
    img.removeEventListener('click', get_user_stats);
    img.addEventListener('click', get_user_stats);
    if (format) {
        img.style.width = `${format.width}px`;
        avatar.style.width = `${format.width}px`;
        img.style.height = `${format.height}px`;
        avatar.style.height = `${format.height}px`;
    }
    if (blob)
        img.src = URL.createObjectURL(blob);
    avatar.appendChild(img);
    return avatar;
}
export function getDefaultAvatar(username = null, format) {
    const avatar = document.createElement("div");
    avatar.classList.add("avatar");
    if (!username)
        username = User.get();
    if (format) {
        if (format.size)
            if (format.size === "large")
                avatar.classList.add("avatar_large");
        if (format.size === "small")
            avatar.classList.add("avatar_small");
        avatar.style.width = `${format.width}px`;
        avatar.style.height = `${format.height}px`;
    }
    avatar.setAttribute("username", username);
    avatar.innerHTML = username.slice(0, 2).toUpperCase();
    avatar.style.backgroundColor = "#652354";
    return avatar;
}
function canvasToBlob(canvas) {
    return new Promise((resolve) => {
        canvas.toBlob((blob) => {
            resolve(blob);
        });
    });
}
export async function setDefaultAvatar(username) {
    if (!username)
        return null;
    let canvas = document.createElement("canvas");
    canvas.height = 128;
    canvas.width = 128;
    let imgctx = canvas.getContext("2d");
    let color_index = Math.floor(Math.random() * defaultAvatarBackgroundColors.length);
    let color = defaultAvatarBackgroundColors[color_index];
    imgctx.fillStyle = color;
    imgctx.fillRect(0, 0, canvas.width, canvas.height);
    let avatar_name = null;
    if (username.length > 1)
        avatar_name = username.slice(0, 2).toUpperCase();
    else
        avatar_name = username[0];
    imgctx.font = "bold 48px Arial";
    imgctx.textAlign = "center";
    imgctx.textBaseline = "middle";
    imgctx.fillStyle = "white";
    const metrics = imgctx.measureText(avatar_name);
    const actualHeight = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;
    imgctx.fillText(avatar_name, canvas.width / 2, canvas.height / 2 + actualHeight / 2 - metrics.actualBoundingBoxDescent);
    const blob = await canvasToBlob(canvas);
    if (blob) {
        await setRemoteAvatar(blob);
        return blob;
    }
    return null;
}
export function reloadAvatar(username) {
    let elements = Array.from(document.getElementsByClassName(`${username}_avatar`));
    const formdata = new FormData();
    formdata.append("username", username);
    fetch(getUrl("accounts/avatar/?username=" + username), {
        method: "GET",
        headers: {
            "X-CSRFToken": getCSRFToken()
        },
        credentials: "include"
    }).then(async (res) => {
        if (!res.ok) {
            if (username === User.get()) {
                return await setDefaultAvatar(username);
            }
            //throw new Error('Avatar not found');
        }
        return res.blob();
    }).then(blob => {
        if (blob) {
            avatar_map[username] = blob;
            const objectUrl = URL.createObjectURL(blob);
            elements.forEach((el) => {
                el.src = objectUrl;
                el.setAttribute("username", username);
                el.removeEventListener('click', get_user_stats);
                el.addEventListener('click', get_user_stats);
            });
        }
    })
        .catch(err => {
        console.log(err);
    });
}
export class Avatar extends HTMLElement {
    user = "";
    constructor() {
        super();
        this.classList.add("avatar");
        this.user = this.getAttribute("user");
    }
    connectedCallback() {
        this.user = this.getAttribute("user");
    }
    disconnectedCallback() { }
}
/**
 *
 * reste a faire sur les avatars :
 *
 * mise en forme css : accueil,
 * methodologie pour les récupérer et les insérer dans le chat
 * modification du css du chat et des chats messages pour intégrer les avatars
 * ajouter des events listeners pour la récupération des scores et l'affichage des informations des joueurs au survol
 * methode de verifications avatar_map... si l'image n'est pas dans avatar_map -> la télécharger aupres du serveur -> si elle n'existe pas affiche l'avatar par defaut
 * modifier dans user details la gestion du css pour le defaut avatar... soit la div contient l'image soit le css par defaut, mais il ne doit pas y avoir deux div differentes
 *
 *
 *
 * reste a faire sur les user details... les afficher, et afficher une icone de modification pour modifier les champs uniquement si l'utilisateur le désire...
 * retravailler la cohérence de l'affichage
 *
 *
 * regler les pb de base de donnée userdetails
 *
 *
 *
 *
 */ 
