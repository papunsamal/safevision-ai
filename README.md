# 🦺 SafeVision AI

### See Risks. Detect Violations. Respond Faster.

**SafeVision AI** is an AI-powered factory safety monitoring system developed for **BPUT Hackathon 2026 — Problem Statement 6: Factory Safety Monitoring & Hazard Detection**.

It uses custom-trained YOLOv8 models to detect Personal Protective Equipment (PPE) violations, fire, and smoke from webcam feeds and recorded videos. Incidents are stored in MySQL, visual evidence is captured, and the React dashboard provides safety monitoring, incident tracking, and compliance reports.

> **Core Principle:** SafeVision AI follows an honesty-first DEMO/REAL architecture. It never presents fabricated detections as genuine AI results.

---

## ✨ Key Features

- 🔴 **Live Webcam Detection:** Real-time YOLO inference with bounding-box overlays.
- 🧠 **Custom YOLOv8 Models:** Separate PPE and fire/smoke detection models.
- 👷 **PPE Compliance:** Supports person, helmet, no-helmet, vest, gloves, boots, and goggles classes when available in the trained model.
- 🔥 **Fire & Smoke Detection:** Tracks continuous hazard events and reduces duplicate incidents across frames.
- 🚨 **Smart Alerts:** MySQL-backed 60-second cooldown to prevent repeated alerts.
- 📸 **Evidence Capture:** Saves JPEG snapshots of detected violations.
- 🗄️ **MySQL Persistence:** Stores incidents, daily statistics, and alert cooldown data.
- 📊 **Real Reports:** Generates compliance statistics and incident trends from database records.
- 🗺️ **Zone-Based Alerts:** Maps camera IDs to physical zones through `configs/zones.json`.
- 🎭 **DEMO / REAL Modes:** Separates sample data from genuine AI inference.
- 📓 **Training Notebooks:** Includes YOLOv8 training notebooks for reproducible model fine-tuning.

---

## 🏗️ System Architecture

```text
┌─────────────────────────┐
│     React Frontend      │
│  Vite + Tailwind CSS    │
└────────────┬────────────┘
             │ HTTP / JSON
             ▼
┌─────────────────────────┐
│     FastAPI Backend     │
│        Port 8000        │
└────────────┬────────────┘
             │
       ┌─────┼───────────┐
       ▼     ▼           ▼
   ┌──────┐ ┌────────┐ ┌─────────┐
   │ YOLO │ │ Rules  │ │  MySQL  │
   │  AI  │ │ Engine │ │Database │
   └──┬───┘ └───┬────┘ └────┬────┘
      └─────────┼───────────┘
                ▼
       ┌─────────────────┐
       │ Alerts & Evidence│
       └─────────────────┘
```

### Detection Workflow

1. Capture frames from a webcam or recorded video.
2. Run the available YOLOv8 detection models.
3. Associate PPE detections with people using spatial matching.
4. Apply compliance rules and temporal confirmation.
5. Generate incidents for confirmed violations.
6. Capture evidence snapshots and save incident records to MySQL.
7. Display monitoring information, alerts, and reports in the dashboard.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite |
| Styling | Tailwind CSS |
| API Communication | Axios |
| Backend | FastAPI, Uvicorn |
| AI Detection | Ultralytics YOLOv8 |
| Video Processing | OpenCV, NumPy |
| Database | MySQL 8.0 |
| Charts | Recharts |
| Dataset Management | Roboflow |
| Model Training | Google Colab, NVIDIA T4 GPU |
| Language | Python, JavaScript |

---

## 📋 Prerequisites

Install the following before running the project:

- Python 3.10 or newer
- Node.js 18 or newer
- MySQL Server 8.0
- Git
- A webcam for live detection (optional)
- Trained YOLOv8 model weights for REAL mode

---

## 🚀 Installation & Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/papunsamal/safevision-ai.git
cd safevision-ai
```

### 2. Create a Python Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Backend Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

**Windows:**

```bash
copy .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Update `.env` with your local configuration:

```env
AI_MODE=DEMO

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=safevision_ai
```

Replace `your_password` with your MySQL password.

**Important:** Never commit `.env` or real database credentials to GitHub.

### 5. Create the MySQL Database

Open MySQL and execute:

```sql
CREATE DATABASE safevision_ai;
```

Ensure that the database connection settings match your `.env` configuration.

Database tables must be created by the application's initialization logic or the project's database setup scripts.

### 6. Start the Backend

Run this command from the project root:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend URL:

`http://localhost:8000`

Interactive API documentation:

`http://localhost:8000/docs`

### 7. Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

`http://localhost:5173`

Keep both backend and frontend terminals running while using the application.

---

## 🧠 AI Models

SafeVision AI is designed to use two custom-trained YOLOv8 models.

| Model | Purpose |
|---|---|
| `ppe_model.pt` | Detects the PPE classes included in the trained model |
| `fire_smoke_model.pt` | Detects fire and smoke classes included in the trained model |

### Model Configuration

Expected model paths:

```text
models/
├── ppe_model.pt
└── fire_smoke_model.pt
```

The model files are not included in the repository by default because trained weights can be large.

### Training Configuration

The included training workflow is designed around:

- YOLOv8n architecture
- Roboflow datasets
- Google Colab
- NVIDIA T4 GPU
- 640 × 640 image size
- 30 training epochs

Actual training results depend on dataset quality, model configuration, and training parameters.

### Training Notebooks

```text
notebooks/
├── ppe_training.ipynb
└── fire_smoke_training.ipynb
```

**Important:** A class can only be detected reliably if the selected model was trained to recognize it. Verify each model's class names before enabling corresponding safety rules.

---

## 🎭 DEMO Mode vs REAL Mode

SafeVision AI separates demonstration data from genuine model inference.

### DEMO Mode

- Intended for demonstrations and interface testing.
- Uses sample data where configured.
- Displays a clear DEMO MODE indicator.
- Does not claim that sample detections are genuine AI predictions.

### REAL Mode

- Requires valid trained model weights.
- Runs actual model inference.
- Uses real video or webcam frames.
- Must not silently replace failed inference with fabricated detections.
- Should report missing models or inference failures clearly.

Set the mode through the environment configuration:

```env
AI_MODE=DEMO
```

For genuine inference:

```env
AI_MODE=REAL
```

**Note:** Automatic fallback to DEMO mode must be implemented explicitly by the application. Confirm the actual startup and error-handling behavior in the code before relying on it.

---

## 📹 Video Assets

Optional sample videos can be placed in:

```text
videos/
├── compliant.mp4
├── violation.mp4
└── fire_smoke.mp4
```

Example usage:

- `compliant.mp4` — workers following PPE requirements.
- `violation.mp4` — footage containing a potential PPE violation.
- `fire_smoke.mp4` — footage containing visible fire or smoke.

These are expected filenames for demonstration assets, not a claim that the files are already included.

Large video files, trained model weights, virtual environments, and generated evidence should be excluded from Git.

---

## 🔌 API Endpoints

The following endpoints describe the intended API interface. Availability depends on the routes implemented in the current codebase.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend and AI health status |
| GET | `/api/videos` | List available videos |
| GET | `/api/detections` | Retrieve or analyze detections, depending on implementation |
| POST | `/api/analyze-video` | Analyze a video and process alerts/evidence |
| GET | `/api/stats` | Safety statistics |
| GET | `/api/workers` | Worker PPE status |
| GET | `/api/alerts` | Retrieve recent incidents |
| GET | `/api/reports` | Compliance and incident reports |
| GET | `/api/cameras` | Camera inventory and zone mapping |
| GET | `/api/live/stream` | Live webcam stream |
| GET | `/videos/*` | Serve configured video assets |
| GET | `/evidence/*` | Serve saved evidence images |

### API Documentation

When the backend is running, visit:

`http://localhost:8000/docs`

### Detection Mode

Where supported by an endpoint, the mode may be specified using a query parameter:

```text
?mode=REAL
```

or:

```text
?mode=DEMO
```

The supported HTTP methods, parameters, and response formats should be verified against the actual FastAPI route definitions.

---

## 🗄️ Database Design

SafeVision AI uses MySQL 8.0 for persistent incident records and reporting.

### Main Tables

#### 1. `incidents`

Stores information about safety incidents:

- Incident type
- Severity
- Incident message
- Camera ID
- Physical zone
- Worker ID, if available
- Evidence image path
- Timestamp

#### 2. `daily_stats`

Stores daily safety statistics, where implemented:

- Total workers
- Compliant workers
- PPE violations
- Fire incidents
- Smoke incidents

#### 3. `alert_cooldowns`

Stores alert deduplication information to reduce repeated notifications for the same event.

### Database Reliability

- Use parameterized SQL queries.
- Keep database credentials in environment variables.
- Handle database connection errors safely.
- Verify that reports use actual database records.
- Ensure that cooldown persistence survives application restarts.

The presence of these table names in the documentation does not itself create them; the application's schema initialization or migration process must do so.

---

## 🗺️ Zone-Based Monitoring

Camera-to-zone mappings are configured through:

```text
configs/zones.json
```

Example zone names:

- Production Area
- Warehouse
- Boiler Area
- Entry Gate
- Live Monitoring

A camera mapping can associate a camera ID with a physical zone so that generated incidents can identify where a potential hazard occurred.

Example configuration structure:

```json
{
  "CAM-01": "Production Area",
  "CAM-02": "Warehouse",
  "CAM-03": "Boiler Area",
  "CAM-04": "Entry Gate",
  "LIVE": "Live Monitoring"
}
```

Use the exact JSON structure expected by the project's zone configuration loader.

---

## ⚖️ PPE Compliance Rules

The compliance engine is intended to associate people with detected PPE objects and evaluate required safety equipment.

Potential PPE classes include:

- Person
- Helmet
- No helmet
- Safety vest
- Gloves
- Safety boots
- Goggles

### Important Limitations

- Missing helmet detection depends on the model's trained classes and compliance logic.
- Missing vest detection cannot be reliably claimed unless the system has a suitable detection or classification method.
- Gloves, boots, and goggles must be supported by the trained model and verified during testing.
- Spatial matching can associate the wrong PPE object with a person in crowded scenes.
- Detection confidence alone does not establish a confirmed safety violation.

Safety rules should be configurable according to the requirements of each monitored zone.

---

## 🚨 Alert Management

The alert manager is designed to reduce duplicate incident creation.

Expected workflow:

```text
AI Detection
     ↓
Compliance Rules
     ↓
Temporal Confirmation
     ↓
Violation Tracker
     ↓
Alert Cooldown Check
     ↓
Evidence Snapshot
     ↓
MySQL Incident Record
     ↓
Dashboard Alert
```

### Alert Cooldown

The configured cooldown is 60 seconds.

The cooldown should prevent repeated alerts for the same tracked event while allowing distinct incidents to be recorded.

Its actual behavior depends on the event key, camera ID, violation type, database state, and alert manager implementation.

---

## 📸 Evidence Capture

When a violation is confirmed, the evidence subsystem is designed to save a JPEG snapshot.

Expected evidence directory:

```text
evidence/
└── alerts/
```

Evidence can help safety officers review incidents and understand the context of an alert.

Recommended practices:

- Include timestamps in evidence metadata.
- Associate each snapshot with its incident record.
- Avoid exposing evidence publicly without access controls.
- Configure retention and cleanup policies.
- Verify that failed snapshot writes are handled safely.

---

## 📊 Dashboard & Reports

The React dashboard is designed to provide:

- Safety overview and incident statistics
- Live monitoring and detection overlays
- PPE compliance status
- Recent and historical alerts
- Incident severity and zone information
- Compliance and incident trend charts

Reports should be generated from real database records in REAL mode. DEMO data should remain clearly identified.

Meaningful trend analysis requires sufficient historical records and consistent incident classification.

---

## 📁 Project Structure

```text
safevision-ai/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── detection.py
│   │   ├── live.py
│   │   ├── alerts.py
│   │   ├── workers.py
│   │   └── cameras.py
│   ├── ai/
│   │   ├── ppe_detector.py
│   │   └── fire_smoke_detector.py
│   ├── rules/
│   │   ├── compliance_engine.py
│   │   ├── zone_rules.py
│   │   └── violation_tracker.py
│   ├── alerts/
│   │   └── alert_manager.py
│   ├── database/
│   │   ├── models.py
│   │   └── database.py
│   └── utils/
│       ├── video.py
│       ├── evidence.py
│       └── logger.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── components/
│       │   ├── Sidebar.jsx
│       │   ├── StatCard.jsx
│       │   └── AlertCard.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── Monitoring.jsx
│       │   ├── Alerts.jsx
│       │   └── Reports.jsx
│       ├── services/
│       │   └── apiClient.js
│       └── App.jsx
│
├── configs/
│   ├── zones.json
│   └── ppe_rules.json
│
├── notebooks/
│   ├── ppe_training.ipynb
│   └── fire_smoke_training.ipynb
│
├── models/
│   ├── ppe_model.pt
│   └── fire_smoke_model.pt
│
├── videos/
│   ├── compliant.mp4
│   ├── violation.mp4
│   └── fire_smoke.mp4
│
└── evidence/
    └── alerts/
```

**Note:** This is the intended project structure. Files and assets may be absent if they have not yet been created locally or committed to the repository.

---

## 🔍 Testing Checklist

Before presenting the project at the hackathon, verify the following.

- [ ] Backend starts without import errors.
- [ ] Frontend installs and builds successfully.
- [ ] MySQL connection succeeds.
- [ ] Required database tables are created.
- [ ] `/health` returns the expected status.
- [ ] DEMO mode is clearly indicated.
- [ ] REAL mode loads the correct model weights.
- [ ] Missing model files produce a clear error.
- [ ] Webcam detection works on supported hardware.
- [ ] Video analysis works with valid video files.
- [ ] Bounding boxes match the actual detections.
- [ ] PPE compliance rules handle missing equipment correctly.
- [ ] Fire/smoke events do not create excessive duplicate incidents.
- [ ] Evidence images are saved and accessible.
- [ ] Incidents persist after a backend restart.
- [ ] Alert cooldown behavior is verified.
- [ ] Reports reflect database records.
- [ ] Invalid requests and database errors are handled safely.

A passing checklist should be based on actual execution and observed results, not documentation alone.

---

## ⚠️ Known Limitations

- The prototype currently targets one local webcam.
- Multi-camera RTSP/CCTV monitoring is planned for future versions.
- CPU inference may be slower than GPU inference.
- Worker tracking uses spatial association rather than advanced re-identification.
- Missing vest detection requires an appropriate model or classification strategy.
- Gloves, boots, and goggles detection depends on model capabilities.
- Report quality depends on the quantity and quality of stored data.
- Training quality depends on dataset coverage and annotation accuracy.
- Actual API behavior depends on the implemented route handlers.

---

## 🔮 Future Scope

- Multi-camera RTSP/CCTV integration
- GPU-accelerated and batch inference
- WebSocket or Server-Sent Events notifications
- Advanced worker tracking and re-identification
- Privacy-preserving face blurring
- SMS and email alerts
- Improved PPE compliance classification
- PostgreSQL support
- Production deployment and monitoring
- Automated testing and model evaluation reports

---

## 🤝 Hackathon Information

**Project:** SafeVision AI

**Event:** BPUT Hackathon 2026

**Problem Statement:** PS6 — Factory Safety Monitoring & Hazard Detection

**Tagline:** See Risks. Detect Violations. Respond Faster.

**Repository:** https://github.com/papunsamal/safevision-ai

Built around an honesty-first DEMO/REAL architecture to support transparent AI demonstrations and factory safety monitoring.

---

## 📜 Disclaimer

SafeVision AI is a hackathon prototype intended to assist with safety monitoring. AI detections may be incorrect or incomplete and should not replace trained safety personnel, certified safety procedures, or independent emergency detection systems.

Always validate model performance under real operating conditions before using the system for safety-critical decisions.
