console.log("hello")
const express = require("express");

const app = express();

app.get("/", (req, res) =>{
    res.send('Hello World!')
})



app.get("/toto", (req, res) =>{
    res.send('Hello Toto!')
})


app.listen(8080, ()=>{
    console.log("express is listening on 8080")
})