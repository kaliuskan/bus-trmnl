from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def get_bus():
    # L'API Grimaud (ne sera pas bloquée ici !)
    url = "https://api-ratp.pierre-grimaud.fr/v3/schedules/bus/123/rue+du+point+du+jour/A"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        schedules = data.get('result', {}).get('schedules', [])

        if not schedules:
            return jsonify({"markup": "Pas d'horaire trouvé."})

        bus1 = schedules[0]['message'].replace("mn", " min").replace("min", " min")
        bus2 = schedules[1]['message'].replace("mn", " min") if len(schedules) > 1 else "--"
        dest = schedules[0]['destination']

        html = f"""
        <div class="layout">
            <div class="title">Bus 123</div>
            <div class="content">
                <div class="item">
                    <span class="label">Vers</span>
                    <span class="value">{dest}</span>
                </div>
                <hr style="opacity:0.2; margin: 5px 0;"> 
                <div class="item">
                    <span class="label">Prochain</span>
                    <span class="value" style="font-size: 30px; font-weight:bold;">{bus1}</span>
                </div>
                <div class="item">
                    <span class="label">Suivant</span>
                    <span class="value">{bus2}</span>
                </div>
            </div>
        </div>
        """
        return jsonify({"markup": html, "refresh_in_seconds": 120})

    except Exception as e:
        return jsonify({"markup": f"Erreur: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
