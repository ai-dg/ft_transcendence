<div align="center">

# ft_transcendence

### Multiplayer Pong Web Application

![Score](https://img.shields.io/badge/Score-121%25-brightgreen)
![42 School](https://img.shields.io/badge/42-School-blue)
![Django](https://img.shields.io/badge/Backend-Django-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

**42 School - Web Development & DevOps Project**

---

### Web Interface Screenshots

<div align="center">

| Game Interface | User Dashboard |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/1aa4d9ed-48d6-4b37-a78c-d31b53f84e5d" alt="Game Interface" width="500"> | <img src="https://github.com/user-attachments/assets/cf7eea26-50fd-4eb7-9938-efa887c71ce7" alt="User Dashboard" width="500"> |

</div>

---

</div>

## Table of Contents

- [Description](#-description)
- [Project Status](#-project-status)
- [Features](#-features)
- [Installation & Launch](#-installation--launch)
- [Makefile Options](#-makefile-options)
- [Technologies Used](#-technologies-used)
- [License](#-license)

---

## ▌ Description  

ft_transcendence is a **multiplayer Pong web application** with advanced features including **WebSocket support**, **AI integration**, **remote authentication**, **live chat**, **tournament system**, and a **secure containerized environment**.  

This project is developed by a **team of four**, including [Christophe Albor Pirame](https://github.com/CronopioSalvaje).

---

## ▌ Project Status ✅  

### ■ **Infrastructure & Core Setup**  

| Component | Description |
|-----------|-------------|
| **Docker** | Multi-container orchestration |
| **Nginx** | Reverse proxy |
| **Gunicorn & Daphne** | Django and WebSockets servers |
| **PostgreSQL** | Database |
| **Redis** | Session and WebSocket management |
| **ELK Stack** | Elasticsearch, Logstash, Kibana for log management |

### ■ **Completed Modules**  

#### **Major Modules**  

| Module | Status | Description |
|--------|--------|-------------|
| Backend Framework | ✅ | Django framework implementation |
| User Management | ✅ | Complete user system with tournament integration |
| Remote Authentication | ✅ | OAuth/remote authentication system |
| Remote Players | ✅ | Multiplayer support for remote connections |
| Live Chat | ✅ | Real-time chat functionality with WebSockets |
| AI Opponent | ✅ | AI implementation for solo mode |
| Log Management | ✅ | ELK stack integration for centralized logging |
| Server-Side Pong & API | ✅ | Server-side game logic with RESTful API |

#### **Minor Modules**  

| Module | Status | Description |
|--------|--------|-------------|
| Frontend Framework | ✅ | Frontend framework/toolkit integration |
| Database | ✅ | PostgreSQL database implementation |
| SSR Integration | ✅ | SSR capabilities for improved performance |  

## ▌ Features  

<div align="center">

| Feature | Description |
|---------|-------------|
| **Full-stack** | Robust architecture with modern technologies |
| **Remote Authentication** | OAuth support for external authentication |
| **Real-time Multiplayer** | WebSocket-based live matches |
| **AI Opponent** | Intelligent AI for solo play |
| **Live Chat** | Real-time messaging functionality |
| **Tournament System** | Complete tournament management |
| **Server-side Logic** | API endpoints for game control |
| **Centralized Logging** | ELK stack for log management |
| **SSR** | Server-Side Rendering for performance |

</div>  

## ▌ Installation & Launch  

### ■ **Prerequisites**

- Docker and Docker Compose installed
- Git installed
- Basic knowledge of environment variables

### ■ **Clone the repository**

```bash
git clone https://github.com/ai-dg/ft_transcendence.git
cd ft_transcendence
```

### ■ **Environment Configuration**

⚠️ **Important**: Before starting the project, you must rename the `.envexample` file to `.env` in the `srcs/` directory:

```bash
cd srcs
cp .envexample .env
```

Then, modify the `.env` file according to your needs (database credentials, ports, OAuth configuration, etc.).

### ■ **Start services with Docker**

```bash
make
```

or

```bash
make up
```

### ■ **Access the application**

The application will be available at `https://localhost:18443/` or `http://localhost:18888/` (set by `PORT_NGINX_HTTPS` / `PORT_NGINX_HTTP` in your `.env` file).

---

## ▌ Makefile Options

### **Startup and Deployment**

| Command | Description |
|---------|-------------|
| `make` or `make up` | Builds and starts all Docker containers |
| `make build` | Builds Docker images without starting them |
| `make re` | Completely rebuilds the project (removes images and restarts) |

### **Stop and Cleanup**

| Command | Description |
|---------|-------------|
| `make down` | Stops all containers without removing volumes |
| `make downv` | Stops containers and removes volumes (database, migrations, venv) |
| `make clean` | Removes all Docker images and cleans the cache |

### **ELK Stack and Logging**

| Command | Description |
|---------|-------------|
| `make generate-log-conf` | Generates Logstash configuration |
| `make import-kibana` | Imports Kibana configurations (index patterns, visualizations) |
| `make wait-kibana` | Waits for Kibana to be ready |
| `make start-logs` | Starts log tracking |
| `make stop-logs` | Stops log tracking |
| `make check-pids` | Checks logging processes |

### **Monitoring**

| Command | Description |
|---------|-------------|
| `make logs` | Displays Nginx container logs |

---

## ▌ Technologies Used  

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Backend** | Python, Django, Django Channels (WebSockets), REST API |
| **Frontend** | JavaScript, HTML, CSS, Server-Side Rendering (SSR) |
| **Database** | PostgreSQL |
| **Services** | Redis, Nginx, Docker, Gunicorn, Daphne |
| **Security** | OAuth (42) |
| **Monitoring & Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) |

</div>  

---

## 📜 License

This project was completed as part of the **42 School** curriculum.  
It is intended for **academic purposes only** and follows the evaluation requirements set by 42.  

Unauthorized public sharing or direct copying for **grading purposes** is discouraged.  
If you wish to use or study this code, please ensure it complies with **your school's policies**.