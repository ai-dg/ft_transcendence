"use strict";
let loginbtn = document.getElementById("logbtn");
let registerbtn = document.getElementById("registerbtn");
let loginfields = document.getElementById("loginfields");
let signupfields = document.getElementById("signupfields");
loginbtn.addEventListener('click', () => {
    loginfields.classList.remove("visually-hidden");
    signupfields.classList.add("visually-hidden");
});
registerbtn.addEventListener('click', () => {
    signupfields.classList.remove("visually-hidden");
    loginfields.classList.add("visually-hidden");
});
