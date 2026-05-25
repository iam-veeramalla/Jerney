# 🛤️ Jerney — Blog Platform

A Gen-Z vibe blog platform built with a 3-tier architecture — React frontend, Node.js backend, and PostgreSQL database.

![Tech Stack](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![Tech Stack](https://img.shields.io/badge/Node.js-20-339933?style=flat-square&logo=node.js)
![Tech Stack](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql)

---

> [!IMPORTANT]
> **Looking for the full DevSecOps implementation?**
> Switch to the [`devops`](../../tree/devops) branch for Docker, Kubernetes (EKS Auto Mode), Terraform, CI/CD with GitHub Actions, container security scanning, and more.
>
> ```bash
> git checkout devops
> ```

---

## ✨ Features

- 📝 Create blog posts with emoji vibes
- ✏️ Edit your existing posts
- 🗑️ Delete posts you're not feeling anymore
- 💬 Comment on posts
- 🎨 Gen-Z dark UI with glassmorphism and gradients

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL   │
│   (React +   │◀────│  (Node.js +  │◀────│              │
│    Nginx)    │     │   Express)   │     │              │
│   Port 80    │     │  Port 5000   │     │  Port 5432   │
└──────────────┘     └──────────────┘     └──────────────┘
```

## 📁 Project Structure

```
Jerney/
├── frontend/                # React (Vite) frontend
│   ├── src/                 # React components & pages
│   ├── nginx.conf           # Nginx config for serving the app
│   └── package.json
├── backend/                 # Node.js Express API
│   ├── src/                 # Routes, DB connection
│   └── package.json
├── deploy/                  # EC2 deployment scripts
│   ├── setup.sh             # One-click EC2 setup script
│   └── jerney-nginx.conf    # Nginx reverse proxy config
└── README.md
```

---

## 🚀 Deploy on AWS EC2

### Prerequisites

- An AWS EC2 instance running **Ubuntu 22.04+**
- Security Group allowing inbound traffic on ports **22** (SSH) and **80** (HTTP)
- SSH access to the instance

### Step 1: Transfer the Code to EC2

```bash
# From your local machine
scp -r -i your-key.pem ./Jerney ubuntu@<EC2_PUBLIC_IP>:~/Jerney
```

### Step 2: SSH into the Instance

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### Step 3: Run the Setup Script

The `deploy/setup.sh` script installs everything and configures the app automatically:

```bash
cd ~/Jerney
chmod +x deploy/setup.sh
./deploy/setup.sh
```

This script will:
1. Update system packages
2. Install **Node.js 20.x**, **PostgreSQL 16**, **Nginx**, and **PM2**
3. Create the database and user
4. Install backend dependencies
5. Build the React frontend
6. Configure Nginx as a reverse proxy
7. Start the backend with PM2 (auto-restarts on crash/reboot)

### Step 4: Access the App

Open your browser and go to:

```
http://<EC2_PUBLIC_IP>
```

### Useful Commands

```bash
pm2 status                          # Check backend status
pm2 logs                            # View backend logs
pm2 restart all                     # Restart backend
sudo systemctl restart nginx        # Restart Nginx
sudo -u postgres psql -d jerney_db  # Connect to database
```

---

## 🧑‍💻 Local Development (Without Docker)

### Prerequisites

- Node.js 20+
- PostgreSQL 16+

### Backend

```bash
cd backend
npm install

# Create a .env file (or export these variables)
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=jerney_user
export DB_PASSWORD=jerney_pass_2026
export DB_NAME=jerney_db
export PORT=5000

npm start
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server starts on `http://localhost:3000` and proxies `/api` requests to the backend at `http://localhost:5000`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/posts` | Get all posts |
| GET | `/api/posts/:id` | Get single post with comments |
| POST | `/api/posts` | Create a new post |
| PUT | `/api/posts/:id` | Update a post |
| DELETE | `/api/posts/:id` | Delete a post |
| GET | `/api/comments/post/:postId` | Get comments for a post |
| POST | `/api/comments` | Create a comment |
| DELETE | `/api/comments/:id` | Delete a comment |


---

## 🌿 Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Source code + EC2 bare-metal deployment |
| `devops` | Full DevSecOps — Docker, Kubernetes (EKS), Terraform, CI/CD pipeline, security scanning |

---

