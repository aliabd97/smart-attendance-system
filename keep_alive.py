import time
import requests
from datetime import datetime

# قائمة خدماتك
SERVICES = [
    "https://attendance-auth-service.onrender.com/health",
    "https://attendance-service-registry.onrender.com/health",
    "https://attendance-student-service.onrender.com/health",
    "https://attendance-course-service.onrender.com/health",
    "https://attendance-attendance-service.onrender.com/health",
    "https://attendance-api-gateway.onrender.com/health"
]

def keep_alive():
    print("🚀 Starting Keep-Alive Script to prevent Render from sleeping...")
    print("Press Ctrl+C to stop.")
    
    while True:
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Pinging services...")
        
        for url in SERVICES:
            try:
                response = requests.get(url, timeout=60)
                status = "✅ Awake" if response.status_code == 200 or response.status_code == 404 else f"⚠️ Status {response.status_code}"
                print(f"   - {url.split('//')[1].split('.')[0]}: {status}")
            except Exception as e:
                print(f"   - {url.split('//')[1].split('.')[0]}: 💤 Waking up... (Error: {str(e)[:20]}...)")
        
        print("⏳ Waiting 10 minutes before next ping...")
        # ننتظر 10 دقائق (600 ثانية) لأن ريندر ينام بعد 15 دقيقة
        time.sleep(600)

if __name__ == "__main__":
    keep_alive()