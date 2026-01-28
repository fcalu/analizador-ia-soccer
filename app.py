import requests
from flask import Flask, render_template
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

BASE_URL = "https://sportia-api.onrender.com/api/v1"

def get_predictions(sport):
    results = []
    # Usamos strings para comparar fechas de forma más segura con la API
    hoy_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    manana_str = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        # 1. Obtener partidos programados
        url_upcoming = f"{BASE_URL}/matches/upcoming?sport={sport}"
        response = requests.get(url_upcoming, timeout=15)
        if response.status_code != 200:
            return results

        matches = response.json()

        for match in matches:
            # Extraemos los primeros 10 caracteres: "2026-01-28"
            fecha_api = match.get("start_time")[:10]

            if fecha_api in [hoy_str, manana_str]:
                payload = {
                    "sport": sport,
                    "league": match.get("league"),
                    "event_id": match.get("event_id"),
                    "home_team": match.get("home"),
                    "away_team": match.get("away")
                }
                
                # 2. Solicitar análisis de la IA
                try:
                    res = requests.post(f"{BASE_URL}/ai/predict", json=payload, timeout=45)
                    if res.status_code == 200:
                        data = res.json()
                        
                        # Buscamos la línea del Pick Principal en el análisis
                        analysis_text = data.get('analysis', '')
                        sug = "Analizando..."
                        for line in analysis_text.split('\n'):
                            if any(x in line for x in ["Pick Principal", "Doble Oportunidad", "Total", "OVER", "UNDER"]):
                                sug = line.replace('#', '').strip()
                                break
                        
                        results.append({
                            "match": data.get('match'),
                            "pick": data.get('tipster_picks', 'No hay pick oficial'),
                            "sugerencia": sug,
                            "confianza": data.get('team_confidence', {}).get('moneyline', 'N/A')
                        })
                except Exception as e:
                    print(f"Error analizando partido {match.get('home')}: {e}")
                    
        return results
    except Exception as e:
        print(f"Error general en {sport}: {e}")
        return []

@app.route('/')
def index():
    # Ejecutamos ambos análisis
    soccer_list = get_predictions("soccer")
    nba_list = get_predictions("nba")
    
    hoy = datetime.now(timezone.utc).strftime('%d/%m/%Y')
    return render_template('index.html', soccer=soccer_list, nba=nba_list, hoy=hoy)

if __name__ == "__main__":
    app.run()