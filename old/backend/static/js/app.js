import { Ball } from "./srcs/Ball.js";
import { Paddle } from "./srcs/Paddle.js";
import { Game } from "./srcs/Game.js";

const ws = new WebSocket("ws://localhost:8001/")

let status = false;
let new_game = document.querySelector("#new_game")

let canvas = document.getElementById("scene");
let chat = document.getElementById("chat")
chat.addEventListener('click',(event)=>{
  let chatbox = document.querySelector(".chatwrapper")
  console.log(chatbox.style.display);
  if (chatbox.style.display ==='block')
    chatbox.style.display ='none'
  else 
    chatbox.style.display ='block'
})
let ctx; 

if (canvas.getContext)
{
  ctx = canvas.getContext("2d");
}
else
{
  console.log("Canvas not supported by your browser")
}

function set_canvas_size(event){

  let SCREEN_HEIGHT = window.innerHeight;
  let  SCREEN_WIDTH = window.innerWidth
  canvas.width = SCREEN_WIDTH * 70 / 100;
  canvas.height = SCREEN_HEIGHT * 85 / 100;
  const rootStyles = document.documentElement.style;
  rootStyles.setProperty('--scene_height', canvas.height);
  rootStyles.setProperty('--scene_width', canvas.width);
  
}
  
set_canvas_size();
window.addEventListener('resize', set_canvas_size)
    
  

let ball = new Ball(ctx);
let player1= new Paddle(10, (canvas.clientHeight / 2 - (85/2)) | 0, ctx)
let player2= new Paddle(canvas.clientWidth - 20, (canvas.clientHeight / 2 - (85/2)) | 0, ctx)

let game = new Game(ball, player1, player2, ctx);

let keys = {ArrowLeft: false, ArrowRight:false, q:false, d:false}


function run()
{
  let data = {yp1:0, yp2:0};

  if(keys.ArrowLeft === true)
    data.yp2 = 1
  else if(keys.ArrowRight === true)
    data.yp2 = -1;
  if(keys.q === true)
    data.yp1 = -1;
  else if(keys.d === true)
    data.yp1 = 1;
  game.update(JSON.stringify(data))
  if (game.run)
    requestAnimationFrame(run)
}



window.addEventListener('keydown', (e) => {
  if (e.target && e.target.tagName === 'INPUT') {
    return;
  }

  e.preventDefault();

  switch(e.key)
  {
    case 'ArrowLeft':  keys.ArrowLeft = true; break;
    case 'ArrowRight': keys.ArrowRight = true; break;
    case 'q': keys.q = true; break;
    case 'd': keys.d = true; break;
    case ' ': game.toogle(game.run); if (game.run){run()}; break;
  }

});

window.addEventListener('keyup', (e) => {
  if (e.target && e.target.tagName === 'INPUT') {
    return;
  }

  e.preventDefault();

  switch(e.key)
  {
    case 'ArrowLeft':  keys.ArrowLeft = false; break;
    case 'ArrowRight': keys.ArrowRight = false; break;
    case 'q': keys.q = false; break;
    case 'd': keys.d = false; break;
  } 

});




new_game.addEventListener('click', (event)=>{
  game.go();
  console.log(game.run);
  fetch("http://localhost:8000/start_game")
    .then(data => data.json())
    .then(data => {
      console.log(data, "blabla");
      run();
    })

})