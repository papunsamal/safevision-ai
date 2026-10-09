import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "http://localhost:8000"
PASS_COUNT = 0
FAIL_COUNT = 0

def test(name, condition, msg=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        print(f"✅ [PASS] {name}")
        PASS_COUNT += 1
    else:
        print(f"❌ [FAIL] {name} -> {msg}")
        FAIL_COUNT += 1

print("\n" + "="*50)
print("🚀 SAFEVISION AI - CRITICAL INTEGRITY CHECK")
print("="*50 + "\n")

# --- TEST 1: Health & Mode Check ---
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    data = r.json()
    
    test("Backend Alive", r.status_code == 200, f"Status: {r.status_code}")
    test("Mode Detected", 'mode' in data, "No 'mode' field in /health")
    
    mode = data.get('mode', '').upper()
    models = data.get('models', {})
    
    if mode == "REAL":
        test("REAL Mode Active", True, "")
        test("PPE Model Loaded", models.get('ppe_model') is True, f"PPE Status: {models.get('ppe_model')}")
        test("Fire/Smoke Model Loaded", models.get('fire_smoke_model') is True, f"Fire Status: {models.get('fire_smoke_model')}")
    elif mode == "DEMO":
        test("DEMO Mode Active (Fallback)", True, "")
        # In DEMO, models might be false or null, which is expected behavior
        print(f"   ℹ️ Running in DEMO mode. Ensure .env has AI_MODE=REAL for full testing.")
        
except Exception as e:
    test("Connection to Backend", False, str(e))
    sys.exit(1)

# --- TEST 2: Database Connectivity ---
try:
    # Try fetching alerts. If DB is down, this usually fails or returns empty safely.
    r_alerts = requests.get(f"{BASE_URL}/api/alerts?mode={mode}", timeout=5)
    test("MySQL Connection OK", r_alerts.status_code == 200, f"Alerts API Status: {r_alerts.status_code}")
    
    if r_alerts.status_code == 200:
        alerts_data = r_alerts.json()
        test("Alerts Structure Valid", isinstance(alerts_data, list), "Response not a list")
except Exception as e:
    test("Database Query Failed", False, str(e))

# --- TEST 3: Video Analysis Logic (The Core) ---
video_name = "violation" # Assuming you have violation.mp4
try:
    start_time = time.time()
    r_det = requests.get(f"{BASE_URL}/api/detections?video={video_name}&mode={mode}", timeout=60)
    duration = time.time() - start_time
    
    test("Video Analysis Endpoint Hit", r_det.status_code == 200, f"Status: {r_det.status_code}")
    
    if r_det.status_code == 200:
        det_data = r_det.json()
        
        # Check keys exist
        test("Detections Key Exists", 'detections' in det_data, "Missing 'detections'")
        test("Workers Key Exists", 'workers' in det_data, "Missing 'workers'")
        test("Violations Key Exists", 'violations' in det_data, "Missing 'violations'")
        test("Stats Key Exists", 'stats' in det_data, "Missing 'stats'")
        
        # Performance Check (CPU bound, so allow up to 30s)
        perf_ok = duration < 30
        test(f"Inference Speed ({duration:.2f}s)", perf_ok, "Too slow (>30s)")
        
        # Content Check (Only if REAL mode)
        if mode == "REAL":
            boxes = det_data.get('detections', [])
            violations = det_data.get('violations', [])
            
            test("Objects Detected in Violation Video", len(boxes) > 0, f"Found {len(boxes)} boxes")
            
            # Check if NO_HELMET is detected
            helmet_violation_found = any('helmet' in v.get('message','').lower() or v.get('type')=='NO_HELMET' for v in violations)
            test("Helmet Violation Detected", helmet_violation_found, f"Violations found: {[v['message'] for v in violations]}")
            
except Exception as e:
    test("Video Analysis Crash", False, str(e))

# --- TEST 4: Error Handling (Robustness) ---
try:
    # Send invalid video name
    r_bad = requests.get(f"{BASE_URL}/api/detections?video=invalid_xyz&mode={mode}", timeout=5)
    # Should return 404 or 400, NOT 500 Internal Server Error
    safe_error = r_bad.status_code in [400, 404]
    test("Invalid Input Handled Safely", safe_error, f"Returned Status: {r_bad.status_code} (Should be 404/400)")
except Exception as e:
    test("Error Handler Network Issue", False, str(e))

# --- SUMMARY ---
print("\n" + "="*50)
total = PASS_COUNT + FAIL_COUNT
print(f"RESULT: {PASS_COUNT}/{total} PASSED | {FAIL_COUNT} FAILED")
print("="*50)

if FAIL_COUNT == 0:
    print("🎉 SYSTEM IS ROBUST AND READY FOR HACKATHON!")
else:
    print("⚠️ SOME ISSUES FOUND. SEE ABOVE FIXES.")