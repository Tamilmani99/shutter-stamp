# Shutter Stamp 📸

**Turn your photographs into nostalgic memories.**

Shutter Stamp is a full-stack image-processing web application that transforms ordinary photographs into vintage-inspired postcards. Users can upload a JPG/JPEG image, choose a visual style, add a location, year, and personal message, and download the resulting photograph.

## ✨ Features

- **Three visual styles:** Lo-Fi, Postcard, and With Love.
- **Random vintage stamps:** Automatically applies one of ten available stamp designs to each processed image.
- **Personalized photographs:** Add a location, year, and custom message.
- **Image validation:** Accepts JPG/JPEG images up to 20 MB.
- **High-quality output:** Preserves image dimensions and exports processed images as JPEG.
- **Image downloads:** Download the generated photograph.
- **Persistent storage:** Stores processed images using a Docker named volume.
- **Responsive interface:** Designed for desktop and mobile screens.

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Image Processing | Pillow |
| Containerization | Docker, Docker Compose |
| Web Server | Nginx |
| Version Control | Git, GitHub |

## 🏗️ Architecture

```text
             User
              |
              v
       React Frontend
        (Nginx :3000)
              |
              | /api/process
              v
       FastAPI Backend
          (:8000)
              |
              v
      Pillow Image Processing
              |
              v
       Processed JPEG Image
              |
              v
       Docker Named Volume
       (Persistent Storage)
```

## 📁 Project Structure

```text
Shutter-Stamp/
│
├── backend/
│   ├── fonts/
│   ├── storage/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.tsx
│   ├── Dockerfile
│   └── package.json
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
```

## 🚀 Run Locally with Docker

### Prerequisites

- Docker Desktop
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Tamilmani99/shutter-stamp.git
cd shutter-stamp
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
MAX_FILE_SIZE=20971520
```

This sets the maximum upload size to 20 MB.

### 3. Build and start the application

```bash
docker compose up -d --build
```

### 4. Access the application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

### 5. Stop the application

```bash
docker compose down
```

The Docker named volume preserves processed images when containers are stopped and removed.

**Important:** Avoid `docker compose down -v` if you want to preserve stored images. That command also removes the named volume.

## 🔍 API Endpoint

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Backend health check |
| POST | `/api/process` | Upload and process an image |

The processing endpoint accepts an image and customization details using multipart form data.

### Image Processing and Privacy

Uploaded images are processed in memory by the backend.

Processed images are returned directly to the user's browser as downloadable files. The application does not permanently store uploaded or generated images on the server.

Previously generated images in the Docker storage volume are retained, but new image processing does not write files to that volume.

## 🔒 Validation and Reliability

- Accepts JPG/JPEG image uploads only.
- Enforces a 20 MB upload limit.
- Validates uploaded files on both frontend and backend.
- Returns appropriate HTTP error responses for invalid uploads.
- Includes a backend health-check endpoint.
- Uses Docker Compose health checks to coordinate service startup.

## 🖼️ Application Preview

*Add screenshots of the application here.*

## 🎯 Project Goals

This project was built to gain practical experience with:

- Full-stack application development.
- REST API development using FastAPI.
- Image processing with Python.
- Docker containerization.
- Multi-container application orchestration.
- Persistent storage using Docker volumes.
- Application health checks and configuration management.
- Git and GitHub workflows.

## 👨‍💻 Author

**Tamilmani**

GitHub: [Tamilmani99](https://github.com/Tamilmani99)

---

*Shutter Stamp — Give your photographs a nostalgic touch.*