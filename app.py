import requests
from flask import Flask, render_template
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

BASE_URL = "https://sportia-api.onrender.com/api/v1"
UPCOMING_URL = f"{BASE_URL}/matches/upcoming?sport=soccer"
PREDICT_URL = f"{BASE_URL}/ai/predict"

@app.route('/')
def index():
    resultados = []
    hoy = datetime.now(timezone.utc).date()
    manana = hoy + timedelta(days=1)
    
    try:
        response = requests.get(UPCOMING_URL, timeout=15)
        matches = response.json()

        for match in matches:
            fecha_match = datetime.fromisoformat(match.get("start_time").replace('Z', '+00:00')).date()

            if fecha_match in [hoy, manana]:
                payload = {
                    "sport": "soccer",
                    "league": match.get("league"),
                    "event_id": match.get("event_id"),
                    "home_team": match.get("home"),
                    "away_team": match.get("away")
                }
                
                res = requests.post(PREDICT_URL, json=payload, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    # Extraer sugerencia del análisis
                    sug = next((line for line in data.get('analysis', '').split('\n') 
                               if "Doble Oportunidad" in line or "Pick Principal" in line), None)
                    
                    resultados.append({
                        "match": data.get('match'),
                        "pick": data.get('tipster_picks'),
                        "sugerencia": sug
                    })
        
        return render_template('index.html', resultados=resultados, hoy=hoy, manana=manana)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run()