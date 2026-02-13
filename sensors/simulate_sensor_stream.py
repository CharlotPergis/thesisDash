import os
import pandas as pd
import random
import time
import joblib
from datetime import datetime

# Get the project root (one level up from sensors/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logs folder inside project root
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "system_log.csv")
os.makedirs(LOG_DIR, exist_ok=True)

# Model path inside project root
MODEL_PATH = os.path.join(BASE_DIR, "model", "rf_model_time_based.joblib")
rf_model = joblib.load(MODEL_PATH)

# System parameters
I_RATED = 20.0
INTERVAL = 1.0  # seconds

# Create CSV header if file does not exist
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=[
        "Timestamp", "Itotal", "Tbreaker", "ThermalSlope",
        "TimeAboveRated", "TimeTempRising", "PredictedState"
    ]).to_csv(LOG_FILE, index=False)

# Initial values
prev_temp = 60.0
TimeAboveRated = 0
TimeTempRising = 0

print("\nStarting real-time simulation...\n")

while True:
    Itotal = round(random.uniform(5, 30), 2)
    Tbreaker = prev_temp + (random.uniform(0.3, 1.5) if Itotal > I_RATED else random.uniform(-0.5, 0.3))
    Tbreaker = round(Tbreaker, 2)
    ThermalSlope = round((Tbreaker - prev_temp) / INTERVAL, 2)

    TimeAboveRated = TimeAboveRated + 1 if Itotal > I_RATED else 0
    TimeTempRising = TimeTempRising + 1 if Tbreaker > prev_temp else 0

    X_live = pd.DataFrame([{
        "Itotal": Itotal,
        "Tbreaker": Tbreaker,
        "ThermalSlope": ThermalSlope,
        "TimeAboveRated": TimeAboveRated,
        "TimeTempRising": TimeTempRising
    }])

    predicted_state = rf_model.predict(X_live)[0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_row = pd.DataFrame([{
        "Timestamp": timestamp,
        "Itotal": Itotal,
        "Tbreaker": Tbreaker,
        "ThermalSlope": ThermalSlope,
        "TimeAboveRated": TimeAboveRated,
        "TimeTempRising": TimeTempRising,
        "PredictedState": predicted_state
    }])

    log_row.to_csv(LOG_FILE, mode="a", header=False, index=False)

    print(f"[{timestamp}] Itotal={Itotal:.2f} A | Tbreaker={Tbreaker:.2f} °C | STATE → {predicted_state}")
    prev_temp = Tbreaker
    time.sleep(INTERVAL)
