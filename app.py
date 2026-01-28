import requests
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

BASE_URL = "https://sportia-api.onrender.com/api/v1"

def get_match_list(sport):
    try:
        hoy_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        manana_str = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = requests.get(f"{BASE_URL}/matches/upcoming?sport={sport}", timeout=20)
        if response.status_code != 200: return []
        
        # Filtramos solo por fecha, sin analizar aún
        return [m for m in response.json() if m.get("start_time")[:10] in [hoy_str, manana_str]]
    except:
        return []

@app.route('/')
def index():
    # Solo obtenemos la LISTA de partidos (es muy rápido)
    soccer_matches = get_match_list("soccer")
    nba_matches = get_match_list("nba")
    return render_template('index.html', soccer=soccer_matches, nba=nba_matches)

@app.route('/predict', methods=['POST'])
def predict():
    # Esta ruta será llamada por JavaScript para cada partido
    payload = request.json
    try:
        res = requests.post(f"{BASE_URL}/ai/predict", json=payload, timeout=60)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()