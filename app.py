import requests
from flask import Flask, render_template
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

BASE_URL = "https://sportia-api.onrender.com/api/v1"

def get_predictions(sport):
    results = []
    hoy = datetime.now(timezone.utc).date()
    manana = hoy + timedelta(days=1)
    
    try:
        # 1. Obtener partidos próximos
        url_upcoming = f"{BASE_URL}/matches/upcoming?sport={sport}"
        response = requests.get(url_upcoming, timeout=15)
        matches = response.json()

        for match in matches:
            # Corregir formato de fecha
            start_time = match.get("start_time").replace('Z', '+00:00')
            fecha_match = datetime.fromisoformat(start_time).date()

            if fecha_match in [hoy, manana]:
                payload = {
                    "sport": sport,
                    "league": match.get("league"),
                    "event_id": match.get("event_id"),
                    "home_team": match.get("home"),
                    "away_team": match.get("away")
                }
                
                # 2. Pedir predicción a la IA
                res = requests.post(f"{BASE_URL}/ai/predict", json=payload, timeout=45)
                if res.status_code == 200:
                    data = res.json()
                    
                    # Extraer el pick principal del análisis
                    analysis = data.get('analysis', '')
                    sug = next((line for line in analysis.split('\n') 
                               if "Pick Principal" in line or "Doble Oportunidad" in line or "Total de puntos" in line), "Ver análisis completo")
                    
                    results.append({
                        "match": data.get('match'),
                        "pick": data.get('tipster_picks'),
                        "sugerencia": sug,
                        "sport": sport
                    })
        return results
    except Exception as e:
        print(f"Error en {sport}: {e}")
        return []

@app.route('/')
def index():
    # Obtener ambos deportes
    soccer_list = get_predictions("soccer")
    nba_list = get_predictions("nba")
    
    hoy = datetime.now(timezone.utc).date()
    return render_template('index.html', soccer=soccer_list, nba=nba_list, hoy=hoy)

if __name__ == "__main__":
    app.run()