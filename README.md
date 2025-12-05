<div align="center">

# ft_transcendence

### Multiplayer Pong Web Application

![Score](https://img.shields.io/badge/Score-121%25-brightgreen)
![42 School](https://img.shields.io/badge/42-School-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
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
| 2FA & JWT | ✅ | Enhanced security with 2FA and JWT tokens |
| Log Management | ✅ | ELK stack integration for centralized logging |
| Server-Side Pong & API | ✅ | Server-side game logic with RESTful API |

#### **Minor Modules**  

| Module | Status | Description |
|--------|--------|-------------|
| Frontend Framework | ✅ | Frontend framework/toolkit integration |
| Database | ✅ | PostgreSQL database implementation |
| Monitoring | ✅ | Application monitoring and observability |
| SSR Integration | ✅ | SSR capabilities for improved performance |  

## ▌ Features  

<div align="center">

| Feature | Description |
|---------|-------------|
| **Full-stack** | Robust architecture with modern technologies |
| **Secure Authentication** | 2FA and JWT token-based security |
| **Remote Authentication** | OAuth support for external authentication |
| **Real-time Multiplayer** | WebSocket-based live matches |
| **AI Opponent** | Intelligent AI for solo play |
| **Live Chat** | Real-time messaging functionality |
| **Tournament System** | Complete tournament management |
| **Server-side Logic** | API endpoints for game control |
| **Centralized Logging** | ELK stack for log management |
| **Monitoring** | Application observability |
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

### ■ **Makefile Options**

<details>
<summary><b>Startup and Deployment</b></summary>

| Command | Description |
|---------|-------------|
| `make` or `make up` | Builds and starts all Docker containers |
| `make build` | Builds Docker images without starting them |
| `make re` | Completely rebuilds the project (removes images and restarts) |

</details>

<details>
<summary><b>Stop and Cleanup</b></summary>

| Command | Description |
|---------|-------------|
| `make down` | Stops all containers without removing volumes |
| `make downv` | Stops containers and removes volumes (database, migrations, venv) |
| `make clean` | Removes all Docker images and cleans the cache |

</details>

<details>
<summary><b>ELK Stack and Logging</b></summary>

| Command | Description |
|---------|-------------|
| `make generate-log-conf` | Generates Logstash configuration |
| `make import-kibana` | Imports Kibana configurations (index patterns, visualizations) |
| `make wait-kibana` | Waits for Kibana to be ready |
| `make start-logs` | Starts log tracking |
| `make stop-logs` | Stops log tracking |
| `make check-pids` | Checks logging processes |

</details>

<details>
<summary><b>Monitoring</b></summary>

| Command | Description |
|---------|-------------|
| `make logs` | Displays Nginx container logs |

</details>

<details>
<summary><b>Update</b></summary>

| Command | Description |
|---------|-------------|
| `make update-static` | Updates static files (installs npm dependencies and collects static files) |

</details>

### ■ **Access the application**

The application will be available at `http://127.0.0.1:8000/` (or according to the `PORT_NGINX_HTTP` configuration in your `.env` file).

---

## ▌ Technologies Used  

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Backend** | Python, Django, Django Channels (WebSockets), REST API |
| **Frontend** | JavaScript, HTML, CSS, Server-Side Rendering (SSR) |
| **Database** | PostgreSQL |
| **Services** | Redis, Nginx, Docker, Gunicorn, Daphne |
| **Security** | JWT (JSON Web Tokens), Two-Factor Authentication (2FA), OAuth |
| **Monitoring & Logging** | ELK Stack (Elasticsearch, Logstash, Kibana) |

</div>  

---

## 📜 License

This project was completed as part of the **42 School** curriculum.  
It is intended for **academic purposes only** and follows the evaluation requirements set by 42.  

Unauthorized public sharing or direct copying for **grading purposes** is discouraged.  
If you wish to use or study this code, please ensure it complies with **your school's policies**.

---

<div align="center">

**Made by the ft_transcendence team**

[Back to Top](#ft_transcendence)

</div>  
