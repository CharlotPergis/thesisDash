from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

# Path to log file
LOG_FILE = os.path.join("logs", "system_log.csv")

@app.route("/")
def dashboard():
    # Read log file
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        # Get last 10 readings for live view
        last_entries = df.tail(10)
    else:
        last_entries = pd.DataFrame(columns=[
            "Timestamp","Itotal","Tbreaker","ThermalSlope",
            "TimeAboveRated","TimeTempRising","PredictedState"
        ])
    
    return render_template("dashboard.html", entries=last_entries.to_dict(orient="records"))

@app.route("/history")
def history():
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        all_entries = df.to_dict(orient="records")
    else:
        all_entries = []
    return render_template("history.html", entries=all_entries)


if __name__ == "__main__":
    app.run(debug=True)
