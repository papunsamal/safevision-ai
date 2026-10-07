# 🦺 SafeVision AI
### See Risks. Detect Violations. Respond Faster.

AI-powered factory safety monitoring system jo **live webcam** aur recorded CCTV/video feeds par **custom-trained YOLO models** se PPE violations (no-helmet), **fire** aur **smoke** detect karta hai — real bounding boxes, real confidence scores, real MySQL database, real evidence snapshots. **Koi fake AI nahi.**

---

## ✨ Features

- 🔴 **Live Webcam Detection** — laptop/USB camera par REAL-time YOLO (MJPEG stream)
- 🧠 **REAL AI MODE** — 2 custom-trained YOLOv8 models:
  - **PPE model** (1,416 images, 11 classes: Person, helmet, no_helmet, vest, gloves, boots, goggles...)
  - **Fire/Smoke model** (Roboflow fire-smoke dataset)
- 🎭 **DEMO MODE** — clearly-labeled sample data jab model/video na ho; zero fake claims
- 👷 **Worker Compliance Engine** — Person ↔ Helmet spatial (IoU) matching se per-worker status
- 🔥 **Fire & Smoke Incidents** — CRITICAL / HIGH severity alerts
- 🚨 **Smart Alerts** — 60-second dedup cooldown (no alert spam)
- 📸 **Evidence Capture** — har violation ka frame snapshot (`evidence/alerts/`)
- 🗄️ **MySQL 8.0 Persistence** — `incidents` + `daily_stats` tables
- 📊 **Real Reports** — compliance & incident trends **MySQL se** (REAL mode mein)
- 🗺️ **Zone Rules** — `configs/zones.json` + `configs/ppe_rules.json` se configurable

---

## 🏗️ Architecture

```
┌──────────────────┐     HTTP/JSON      ┌─────────────────────────┐
│  React Frontend  │ ◄─────────────────►│  FastAPI Backend (:8000)│
│ (Vite + Tailwind)│                    │                         │
└──────────────────┘                    └───────────┬─────────────┘
                                                    │
                 ┌──────────────┬───────────────────┼──────────────┐
                 ▼              ▼                   ▼              ▼
             ai/ (YOLO)     rules/             database/        utils/
             ppe + fire/    compliance         MySQL 8.0        video,
             smoke detect   engine (IoU)       incidents +      evidence,
                            zone rules         daily_stats      logger
                            violation tracker
                 ▲
                 │
        alerts/ (alert manager — dedup cooldown)
```

**backend/ structure:**
```
backend/
├── main.py            # App entry, routers, static serving, DB init
├── config.py          # env-based settings (AI_MODE, MySQL, paths)
├── api/               # detection, alerts, workers, cameras, live
├── ai/                # ppe_detector, fire_detector, smoke_detector, tracker
├── rules/             # compliance_engine, zone_rules, violation_tracker
├── alerts/            # alert_manager (60-sec dedup)
├── database/          # models (schema) + database (MySQL CRUD)
└── utils/             # video sampling, evidence snapshots, logger
```

---

## 🚀 Setup

### Prerequisites
Python 3.10+ • Node 18+ • MySQL 8.0

### 1. Backend
```bash
python -m venv venv
venv\Scripts\activate                 # Windows
pip install -r requirements.txt

cp .env.example .env                  # MySQL password + AI_MODE set karo
python -m uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev                           # http://localhost:5173
```

### 3. Models (REAL mode)
- `models/ppe_model.pt` — PPE model (gitignored, size limit)
- `models/fire_smoke_model.pt` — Fire/Smoke model (gitignored)
- Models ke bina system **automatically DEMO MODE** mein chalta hai (honestly labeled)

### 4. Demo videos (gitignored)
`videos/compliant.mp4`, `videos/violation.mp4`, `videos/fire_smoke.mp4`
Free stock: pexels.com → "construction workers" / "fire smoke"

---

## 🧠 Model Training (reproduce karne ke liye)

| | PPE Model | Fire/Smoke Model |
|---|---|---|
| Dataset | Roboflow PPE — 1,416 images, 11 classes | Roboflow "Fire and smoke" (YOLOv8) |
| Base | YOLOv8n | YOLOv8n |
| Training | Colab T4 GPU, 30 epochs, imgsz 640 | Colab T4 GPU, 30 epochs, imgsz 640 |
| Metrics | **Precision 0.75 • Recall 0.53 • mAP50 0.56** | dataset-dependent |

Recipe: `!pip install ultralytics` → `model.train(data="data.yaml", epochs=30, imgsz=640)` → `best.pt` rename karke `models/` mein.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Mode (DEMO/REAL) + models status + supported classes |
| GET | `/api/live/stream?camera=0` | **Live webcam MJPEG stream with boxes** |
| GET | `/api/stats` | Worker/violation/fire/smoke stats |
| GET | `/api/workers` | Per-worker PPE status |
| GET | `/api/alerts` | Incidents (MySQL se, evidence URLs ke saath) |
| GET | `/api/reports` | REAL: MySQL trends • DEMO: sample |
| GET | `/api/cameras` | Camera list |
| GET | `/api/detections?video=&mode=` | Video analysis → bounding boxes |
| POST | `/api/analyze-video?video=` | Full analysis + incidents + evidence |
| GET | `/videos/*`, `/evidence/*` | Static media |

---

## 🎭 DEMO vs REAL — Honesty Policy

- **DEMO MODE:** amber banner, clearly labeled sample data
- **REAL MODE:** tabhi enable hota hai jab trained model maujood ho
- Vest **absence** ko violation **nahi** bola jata (dataset limitation — sirf informational)
- System kabhi fake detections claim **nahi** karta

---

## ⚠️ Honest Limitations

- Dataset mein explicit "no-vest" class nahi → vest sirf informational
- CPU inference ~10-20 sec/video; live webcam ~2-4 FPS (production: GPU)
- Reports trends ko 1+ din ka data chahiye (shuru mein sparse)
- Recorded videos + webcam; external CCTV ke liye RTSP future scope

## 🔮 Future Scope

RTSP/CCTV streams • GPU inference • Socket.IO push alerts • Worker tracking (tracker.py ready) • PostgreSQL • Face blurring (privacy) • SMS/WhatsApp alerts

---

## 🛠️ Tech Stack

React • Vite • Tailwind CSS • FastAPI • Ultralytics YOLOv8 • OpenCV • MySQL 8.0 • Roboflow • Google Colab

---

**SafeVision AI — Hackathon 2026** 🦺⚡