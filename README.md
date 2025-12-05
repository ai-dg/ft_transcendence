# ft_transcendence - Multiplayer Pong Web App  

<img src="https://github.com/user-attachments/assets/1aa4d9ed-48d6-4b37-a78c-d31b53f84e5d" width="500" height="500">

<img src="https://github.com/user-attachments/assets/cf7eea26-50fd-4eb7-9938-efa887c71ce7" width="500" height="500">



📌 **42 School - Web Development & DevOps Project**  

## ▌ Description  
ft_transcendence is an ongoing project aimed at creating a **multiplayer Pong web application** with advanced features such as **WebSocket support**, **AI integration**, and a **secure containerized environment**.  

This project is developed by a **team of four**, including [Christophe Albor Pirame](https://github.com/CronopioSalvaje).  

## ▌ Project Status 🚧  
### ■ **Docker infrastructure set up**, including:  
▸ **Nginx** (reverse proxy)  
▸ **Gunicorn & Daphne** (for Django and WebSockets)  
▸ **PostgreSQL** (database)  
▸ **Redis** (session and WebSocket management)  

### ■ **Backend development in progress**:  
▸ WebSocket support for real-time connections  
▸ **AI implementation** for solo mode  
▸ **Basic Pong game**, but no advanced features yet  

⚠ **The project is still in development, and many features are not finalized.**  

## ▌ Objectives  
✔ Build a **full-stack** application with a robust architecture  
✔ Implement **secure authentication**  
✔ Manage **real-time matches** between players  
✔ Develop an **AI opponent** for solo play  
✔ Add a **ranking and statistics system**  

## ▌ Installation & Launch  
### ■ **Clone the repository**
```sh
git clone https://github.com/ai-dg/ft_transcendence.git  
cd ft_transcendence  
```

### ■ **Environnement file**
Add .env file in srcs/ with the any following credentials:
```env
HOME=$HOME
POSTGRES_USER="user"
POSTGRES_PASSWORD="password"
POSTGRES_DB="database"
DJANGO_ENV=DEV
```

### ■ **Start the services with Docker**
```sh
make
```

### ■ **Access the application**  
The app will be available at `http://127.0.0.1:8000/`.  

## ▌ Technologies Used  
▸ **Backend**: Python, Django, Django Channels (WebSockets)  
▸ **Frontend**: JavaScript, HTML, CSS  
▸ **Database**: PostgreSQL  
▸ **Services**: Redis, Nginx, Docker, Gunicorn  

## 📜 License

This project was completed as part of the **42 School** curriculum.  
It is intended for **academic purposes only** and follows the evaluation requirements set by 42.  

Unauthorized public sharing or direct copying for **grading purposes** is discouraged.  
If you wish to use or study this code, please ensure it complies with **your school's policies**.  
