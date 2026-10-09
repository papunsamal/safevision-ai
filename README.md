# 🦺 SafeVision AI
### See Risks. Detect Violations. Respond Faster.

**SafeVision AI** is an AI-powered factory safety monitoring system developed for **BPUT Hackathon 2026 — Problem Statement 6: Factory Safety Monitoring & Hazard Detection**.

It uses custom-trained YOLOv8 models to detect PPE violations, including missing helmets, fire, and smoke in live webcam feeds and recorded videos. The system generates location-aware alerts, captures visual evidence, stores incidents in MySQL, and provides compliance analytics through an interactive dashboard.

Built with an **honesty-first architecture**, SafeVision AI clearly distinguishes demonstration data from real AI inference. DEMO mode is labeled, and REAL mode never substitutes fabricated detections when inference fails.

**Team Name:** InovaBuild  
**Team ID:** BH26PS06T051

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#️-system-architecture)
- [Technology Stack](#️-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation and Setup](#-installation-and-setup)
- [AI Models and Training](#-ai-models-and-training)
- [API Reference](#-api-reference)
- [Database Schema](#️-database-schema)
- [DEMO vs REAL Mode](#-demo-vs-real-mode)
- [Known Limitations](#️-known-limitations)
- [Future Scope](#-future-scope)
- [Project Structure](#-project-structure)
- [Contributing and Attribution](#-contributing-and-attribution)

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔴 Live Webcam Detection | Real-time YOLO inference with server-side bounding boxes through an MJPEG stream. |
| 🧠 Custom-Trained AI Models | Separate YOLOv8 models for PPE detection and fire/smoke detection. |
| 👷 PPE Compliance Analysis | Spatial matching between people and detected safety equipment using IoU and positional rules. |
| 🔥 Fire and Smoke Tracking | Counts continuous fire/smoke events as incidents rather than counting every sampled frame. |
| 🚨 Smart Alert Management | MySQL-backed 60-second deduplication with camera, zone, rule, and worker context. |
| 📸 Visual Evidence | Saves JPEG snapshots of detected violations in `evidence/alerts/`. |
| 🗄️ MySQL Persistence | Stores incidents, daily statistics, and alert cooldown state. |
| 📊 Analytics Dashboard | Displays compliance trends and incident reports using database aggregations. |
| 🎭 DEMO and REAL Modes | Clearly separates sample data from actual model inference. |
| 🗺️ Zone-Based Monitoring | Associates cameras and incidents with configured physical locations. |
| 📓 Reproducible Training | Includes Jupyter notebooks for training the PPE and fire/smoke models. |

---

## 🏗️ System Architecture

```text
┌─────────────────────────────┐
│     React Frontend          │
│   Vite + Tailwind CSS       │
└──────────────┬──────────────┘
               │ HTTP / JSON
               ▼
┌─────────────────────────────┐
│      FastAPI Backend        │
│       Port: 8000            │
└──────────────┬──────────────┘
               │
       ┌───────┼────────┬──────────┐
       ▼       ▼        ▼          ▼
    AI/YOLO   Rules   Database   Utilities
       │       │        │          │
       ▼       ▼        ▼          ▼
      PPE   Compliance  MySQL    Video Frames
   Fire/Smoke  Engine   Incidents Evidence
                       Statistics Logging
                          │
                          ▼
                    Alert Manager
                  60s Deduplication
                          │
                          ▼
                  Safety Incidents
```

### Backend Modules

| Module | Responsibility |
|---|---|
| `backend/main.py` | Application entry point, CORS, static files, and database initialization. |
| `backend/config.py` | Environment variables and application settings. |
| `backend/api/detection.py` | Video analysis, frame merging, event counting, and detection timelines. |
| `backend/api/live.py` | Webcam capture and MJPEG streaming with detection overlays. |
| `backend/api/alerts.py` | Incident retrieval and reporting endpoints. |
| `backend/api/workers.py` | Worker PPE compliance and statistics. |
| `backend/api/cameras.py` | Camera inventory and zone assignments. |
| `backend/ai/ppe_detector.py` | PPE model loading and inference. |
| `backend/ai/fire_smoke_detector.py` | Fire and smoke model loading and inference. |
| `backend/rules/compliance_engine.py` | Spatial equipment matching and compliance rules. |
| `backend/rules/zone_rules.py` | Camera-to-zone mapping. |
| `backend/rules/violation_tracker.py` | Recent incidents and persistence. |
| `backend/alerts/alert_manager.py` | Alert severity, cooldown, and deduplication. |
| `backend/database/database.py` | Database connections and query execution. |
| `backend/database/models.py` | Database schema definitions. |
| `backend/utils/video.py` | Frame sampling and video-processing helpers. |
| `backend/utils/evidence.py` | Evidence snapshot generation. |
| `backend/utils/logger.py` | Structured application logging. |

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite 8, Tailwind CSS |
| Backend | Python, FastAPI, Uvicorn |
| AI / Computer Vision | Ultralytics YOLOv8, OpenCV, NumPy |
| Database | MySQL 8.0, mysql-connector-python |
| Data Visualization | Recharts |
| Dataset Annotation | Roboflow |
| Model Training | Google Colab, NVIDIA T4 GPU |
| Runtime | Python 3.10+, Node.js 18+ |

---

## 📋 Prerequisites

Before running SafeVision AI, install the following:

- Python 3.10 or later
- Node.js 18 or later
- npm
- MySQL 8.0
- Git
- A webcam for live detection (optional)
- Trained YOLOv8 model files for REAL mode

---

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/papunsamal/safevision-ai.git
cd safevision-ai
```

### 2. Set Up the Python Backend

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create your environment file:

```bash
copy .env.example .env
```

Open `.env` and configure the required settings, including your MySQL credentials and AI mode.

Example configuration:

```env
AI_MODE=DEMO

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=safevision
```

**Important:** Replace the example password with your own MySQL password. Never commit `.env` or real credentials to GitHub.

Use `AI_MODE=REAL` only after placing the trained model files at the expected paths.

### 4. Start the Backend

From the project root:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend API:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### 5. Set Up the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend URL displayed by Vite, normally:

```text
http://localhost:5173
```

Keep both the backend and frontend terminals running.

---

## 🧠 AI Models and Training

SafeVision AI is designed to use two domain-specific YOLOv8 models.

| Parameter | PPE Model | Fire/Smoke Model |
|---|---|---|
| Architecture | YOLOv8n | YOLOv8n |
| Dataset | Industrial PPE | Fire and Smoke |
| Dataset Size | 1,416 annotated images | Approximately 2,000 frames |
| Training Platform | Google Colab T4 GPU | Google Colab T4 GPU |
| Epochs | 30 | 30 |
| Image Size | 640 × 640 | 640 × 640 |
| Precision | 0.75 | Dataset-dependent |
| Recall | 0.53 | Dataset-dependent |
| mAP@50 | 0.56 | Dataset-dependent |
| Notebook | `notebooks/ppe_training.ipynb` | `notebooks/fire_smoke_training.ipynb` |

*Reported metrics are project-provided values and should be verified against the actual training results before evaluation.*

### PPE Model Classes

The reported PPE model classes are:

```text
Person
Helmet
No Helmet
None
Vest
Gloves
Boots
Goggles
No Boots
No Gloves
No Goggle
```

### Fire and Smoke Model Classes

```text
Fire
Smoke
```

### Model File Locations

Large model files are excluded from GitHub and must be obtained separately.

Place the files at these paths:

```text
models/
├── ppe_model.pt
└── fire_smoke_model.pt
```

Required video assets, if used, should be placed in:

```text
videos/
├── compliant.mp4
├── violation.mp4
└── fire_smoke.mp4
```

If the model files are unavailable, use the clearly labeled DEMO mode.

**Why custom-trained models?**

Generic COCO-pretrained YOLO models do not provide all the specialized PPE and fire/smoke classes required by this project. Domain-specific training allows the system to learn the relevant safety categories from appropriately annotated industrial imagery.

---

## 🔌 API Reference

The backend exposes the following endpoints. Exact behavior should be verified against the running application and its route definitions.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | System health, active mode, and model availability. |
| GET | `/api/videos` | Lists available MP4 video files. |
| GET | `/api/detections?video=&mode=` | Analyzes a video and returns detections and statistics. |
| POST | `/api/analyze-video?video=&mode=` | Runs video analysis and triggers configured incident-processing side effects. |
| GET | `/api/stats?mode=` | Returns worker, violation, and incident statistics. |
| GET | `/api/workers?mode=` | Returns worker PPE compliance information. |
| GET | `/api/alerts?mode=` | Retrieves recent incidents and evidence URLs. |
| GET | `/api/reports?mode=` | Returns compliance and incident trend data. |
| GET | `/api/cameras` | Lists configured cameras and zone assignments. |
| GET | `/api/live/stream?camera=0` | Streams live webcam frames with detection overlays. |
| GET | `/videos/*` | Serves available video files. |
| GET | `/evidence/*` | Serves captured evidence images. |

### Mode Selection

Endpoints that support mode selection accept:

```text
?mode=DEMO
```

or:

```text
?mode=REAL
```

When the parameter is omitted, the backend uses its configured default.

### Example Requests

Check system health:

```bash
curl http://localhost:8000/health
```

List available videos:

```bash
curl http://localhost:8000/api/videos
```

Retrieve incidents:

```bash
curl "http://localhost:8000/api/alerts?mode=REAL"
```

Get reporting data:

```bash
curl "http://localhost:8000/api/reports?mode=REAL"
```

Analyze a video:

```bash
curl -X POST "http://localhost:8000/api/analyze-video?video=violation.mp4&mode=REAL"
```

**Response integrity:** Responses should identify their operating mode so consumers can distinguish real inference results from demonstration fixtures.

---

## 🗄️ Database Schema

SafeVision AI uses MySQL 8.0 to persist incident information, reporting statistics, and alert cooldown state.

### 1. `incidents`

Stores detected safety events.

| Column | Description |
|---|---|
| `id` | Unique incident identifier. |
| `type` | Incident category, such as PPE, FIRE, or SMOKE. |
| `severity` | LOW, MEDIUM, HIGH, or CRITICAL. |
| `message` | Description of the incident. |
| `camera` | Camera identifier. |
| `zone` | Physical location of the incident. |
| `worker_id` | Worker identifier, when applicable. |
| `frame_url` | Path to the evidence snapshot. |
| `created_at` | Incident creation timestamp. |

### 2. `daily_stats`

Stores daily aggregated compliance statistics.

| Column | Description |
|---|---|
| `stat_date` | Reporting date and primary key. |
| `total_workers` | Total workers counted. |
| `compliant_workers` | Workers meeting applicable compliance rules. |
| `ppe_violations` | PPE violation count. |
| `fire_incidents` | Fire incident count. |
| `smoke_incidents` | Smoke incident count. |
| `updated_at` | Last update timestamp. |

### 3. `alert_cooldowns`

Stores deduplication state so repeated events do not continuously generate alerts.

| Column | Description |
|---|---|
| `ckey` | Composite alert key. |
| `last_seen` | Last-seen Unix timestamp. |

The schema is initialized by the backend during startup, according to the project's database initialization logic.

If MySQL is unavailable, the application is designed to degrade gracefully where supported. Database-dependent features may return incomplete or empty results until connectivity is restored.

---

## 🎭 DEMO vs REAL Mode

SafeVision AI separates sample data from actual model inference.

| Aspect | DEMO Mode | REAL Mode |
|---|---|---|
| Purpose | Demonstration and UI testing | Actual AI inference |
| Data Source | Sample fixtures | YOLOv8 model output |
| UI Indicator | Visible DEMO MODE banner | Normal operational interface |
| Model Requirement | Trained models not required | Required model files must be available |
| Detection Failure | Sample behavior, clearly labeled | Must not silently substitute demo detections |
| Reporting | Demonstration data may be used | Based on actual persisted analysis data |
| Live Webcam | Not a substitute for real inference | Requires an accessible camera and working model |

### REAL Mode Requirements

The expected model files are:

```text
models/ppe_model.pt
models/fire_smoke_model.pt
```

File existence alone does not prove that a model is valid. REAL mode must also handle model-loading failures, inference errors, unavailable cameras, and missing video assets honestly.

### PPE Compliance Policy

The reported training classes do not include an explicit `no_vest` class. Therefore, vest absence must not be automatically treated as a confirmed violation.

The current policy focuses on helmet non-compliance when the applicable model outputs and compliance rules support that conclusion.

This reduces unsupported violation claims and helps maintain trust in the system's results.

---

## ⚠️ Known Limitations

| Limitation | Current Impact |
|---|---|
| No `no_vest` class | Missing vests cannot reliably be confirmed as violations. |
| CPU-bound inference | Recorded video analysis may take approximately 10–20 seconds per clip. |
| Limited live processing speed | Webcam processing may run at approximately 2–4 FPS, depending on hardware and scene complexity. |
| Limited reporting history | Trend charts may show insufficient data when few analyses have been recorded. |
| Single-camera scope | Current prototype focuses on a local webcam and prerecorded MP4 files. |
| Position-based worker matching | Occlusion and rapid movement may fragment worker identities. |
| Dataset-dependent accuracy | Real-world performance may differ from training and validation results. |

Performance estimates depend on hardware, video duration, resolution, and model configuration.

---

## 🔮 Future Scope

| Priority | Enhancement | Proposed Implementation |
|---|---|---|
| High | Multi-camera RTSP support | Add asynchronous camera ingestion and shared detector instances. |
| High | GPU-accelerated inference | Deploy with CUDA-enabled inference infrastructure. |
| Medium | Real-time push notifications | Add Socket.IO or SSE event delivery from alert callbacks. |
| Medium | Improved worker tracking | Introduce learned re-identification embeddings. |
| Low | Privacy-preserving evidence | Add face blurring before saving snapshots. |
| Low | SMS and email escalation | Integrate notification adapters based on severity. |
| Low | Database portability | Introduce a repository abstraction supporting additional SQL databases. |

These are planned improvements, not claims of already implemented functionality.

---

## 📁 Project Structure

```text
safevision-ai/
│
├── backend/
│   ├── ai/
│   │   ├── ppe_detector.py
│   │   └── fire_smoke_detector.py
│   │
│   ├── alerts/
│   │   └── alert_manager.py
│   │
│   ├── api/
│   │   ├── detection.py
│   │   ├── live.py
│   │   ├── alerts.py
│   │   ├── workers.py
│   │   └── cameras.py
│   │
│   ├── database/
│   │   ├── models.py
│   │   └── database.py
│   │
│   ├── rules/
│   │   ├── compliance_engine.py
│   │   ├── zone_rules.py
│   │   └── violation_tracker.py
│   │
│   ├── utils/
│   │   ├── video.py
│   │   ├── evidence.py
│   │   └── logger.py
│   │
│   ├── config.py
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── vite.config.js
│
├── configs/
│   ├── ppe_rules.json
│   └── zones.json
│
├── models/                     # Local model weights
├── videos/                     # Local video assets
├── evidence/                   # Generated evidence
├── notebooks/
│   ├── ppe_training.ipynb
│   └── fire_smoke_training.ipynb
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

*This structure documents the intended project layout; actual filenames should match the repository.*

Large binary assets are excluded from version control to keep the repository manageable. Model weights and video assets can be distributed separately, subject to dataset and competition licensing requirements.

---

## 🔒 Security and Reliability

- Keep database credentials and other secrets in `.env`.
- Never commit real passwords, API keys, or private credentials.
- Use parameterized SQL queries for database operations.
- Validate uploaded video files and enforce reasonable file-size limits.
- Handle unavailable cameras and invalid model files without crashing the application.
- Keep DEMO and REAL data clearly distinguishable.
- Verify that evidence URLs and database records refer to actual generated artifacts.

---

## 🤝 Contributing and Attribution

SafeVision AI was developed for **BPUT Hackathon 2026 — Problem Statement 6**.

The project uses third-party libraries and datasets that remain subject to their respective licenses and attribution requirements. Dataset sources and training details should be documented in the corresponding notebooks.

Model weights may be distributed separately according to the team's access arrangements, dataset licensing, and competition guidelines.

Contributions that improve detection reliability, reporting accuracy, safety compliance, and system transparency are welcome.

---

## 🦺 SafeVision AI

**See Risks. Detect Violations. Respond Faster.**

*Built by Team InovaBuild for BPUT Hackathon 2026.*