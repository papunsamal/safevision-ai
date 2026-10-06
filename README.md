# 🦺 SafeVision AI
### See Risks. Detect Violations. Respond Faster.

AI-powered factory safety monitoring system jo CCTV/video feeds par **custom-trained YOLO model** se PPE violations (no-helmet, no-vest), fire aur smoke detect karta hai — real bounding boxes, real confidence scores, real database. **Koi fake AI nahi.**

---

## ✨ Features

- 🧠 **REAL AI MODE** — Custom-trained YOLOv8 PPE model (1,416 images, 11 classes) se live detection
- 🎭 **DEMO MODE** — Clearly-labeled sample data (jab model/video na ho), zero fake claims
- 👷 **Worker Compliance Engine** — Person ↔ Helmet/Vest spatial (IoU) matching se per-worker status
- 🎯 **Live Bounding Boxes** — Video par overlay with confidence scores
- 🚨 **Smart Alerts** — 60-second dedup cooldown (alert spam nahi)
- 📸 **Evidence Capture** — Har violation ka frame snapshot (`evidence/alerts/`)
- 🗄️ **MySQL 8.0 Persistence** — Incidents restart ke baad bhi safe
- 🗺️ **Zone Rules** — `configs/zones.json` + `configs/ppe_rules.json` se configurable
- 📊 **Dashboard & Reports** — Compliance trend + incident analytics

---

## 🏗️ Architecture

```
┌─────────────────┐      HTTP/JSON      ┌──────────────────────┐
│  React Frontend │ ◄──────────────────►│  FastAPI Backend     │
│  (Vite+Tailwind)│                     │  (port 8000)         │
└─────────────────┘                     └──────────┬───────────┘
                                                   │
                          ┌────────────┬───────────┼───────────┐
                          ▼            ▼           ▼           ▼
                      ai/ (YOLO)   rules/     database/    utils/
                      detectors    compliance  MySQL 8.0    video,
                                   engine      incidents    evidence
```

**backend/ structure:**
```
backend/
├── main.py            # FastAPI app + routers + static serving
├── config.py          # env-based settings
├── api/               # routers: detection, alerts, workers, cameras
├── ai/                # ppe/fire/smoke detectors + centroid tracker
├── rules/             # compliance engine, zone rules, violation tracker
├── alerts/            # alert manager (dedup cooldown)
├── database/          # MySQL schema + CRUD
└── utils/             # video sampling, evidence snapshots, logger
```

---

## 🚀 Setup

### Prerequisites
- Python 3.10+, Node 18+, MySQL 8.0

### 1. Backend
```bash
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt

cp .env.example .env             # apna MySQL password daalo
python -m uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

### 3. Model (REAL mode ke liye)
`models/ppe_model.pt` rakho (gitignored — size limit).
Model ke bina system automatically **DEMO MODE** mein chalta hai (honestly labeled).

### 4. Demo videos
`videos/compliant.mp4` aur `videos/violation.mp4` rakho (gitignored).
Free stock: pexels.com → "construction workers".

---

## 🧠 Model Training

| Item | Detail |
|---|---|
| Dataset | Roboflow PPE — 1,416 images, 11 classes |
| Base model | YOLOv8n (pretrained) |
| Training | Google Colab, T4 GPU, 30 epochs, imgsz 640 |
| **Metrics** | **Precision 0.75 • Recall 0.53 • mAP50 0.56** |
| Classes | Person, helmet, no_helmet, none, vest, boots, no_boots, gloves, no_gloves, goggles, no_goggle |

Reproduce karne ke liye: `notebooks/model_testing.ipynb` + Colab recipe (ultralytics train).

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Mode (DEMO/REAL) + model status + supported classes |
| GET | `/api/stats` | Worker/violation stats |
| GET | `/api/workers` | Per-worker PPE status |
| GET | `/api/alerts` | Incidents (MySQL se) |
| GET | `/api/reports` | Trend analytics |
| GET | `/api/cameras` | Camera list |
| GET | `/api/detections?video=&mode=` | Video analysis → boxes |
| POST | `/api/analyze-video?video=` | Full analysis + incidents + evidence |
| GET | `/videos/*`, `/evidence/*` | Static media |

---

## 🎭 DEMO vs REAL — Honesty Policy

- **DEMO MODE:** sample data, amber banner ke saath clearly labeled
- **REAL MODE:** tabhi enable hota hai jab trained model maujood ho
- System kabhi bhi fake detections claim **nahi** karta

---

## ⚠️ Honest Limitations

- Dataset mein explicit "no-vest" class nahi → vest-absence sirf tab flag hota hai jab vest detections present hon
- Fire/smoke model abhi trained nahi (architecture ready — model drop karo, on)
- CPU inference ~10-20 sec/video (production: GPU + RTSP streams)

## 🔮 Future Scope

RTSP/CCTV live streams • Fire-smoke model • Socket.IO real-time alerts •
PostgreSQL upgrade path • Face blurring (privacy) • SMS/WhatsApp alerts

---

## 🛠️ Tech Stack

React • Vite • Tailwind CSS • FastAPI • Ultralytics YOLOv8 • OpenCV •
MySQL 8.0 • Roboflow • Google Colab

---

**SafeVision AI — Hackathon 2026** 🦺⚡