from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Clé API IDFM
PRIM_KEY = "CzyhmgXXqA0IfjxTt0pAFp3LVr5m2mqY"

@app.route('/')
def get_bus():
    # Méthode DIRECTE : On demande les horaires du bus 123 aux coordonnées GPS exactes
    # Plus besoin de chercher l'ID de l'arrêt, c'est automatique.
    # Coordonnées : 2.2527 (Lon), 48.8328 (Lat) ~ Rue du Point du Jour
    url = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/coords/2.2527;48.8328/stop_schedules?line_id=line:IDFM:C01375"
    headers = {"apiKey": PRIM_KEY}
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        
        # On vérifie si on a une réponse
        if not data.get('stop_schedules'):
             return jsonify({"markup": "Pas d'horaires trouvés (GPS)"})

        # On prend le premier résultat (le plus proche)
        schedules = data['stop_schedules'][0]['date_times']
        
        departs = []
        for s in schedules:
            # Format : 20231226T184500
            date_time_str = s['date_time']
            # On parse proprement l'heure
            dt = datetime.strptime(date_time_str, "%Y%m%dT%H%M%S")
            departs.append(dt.strftime("%H:%M"))

        bus1 = departs[0] if len(departs) > 0 else "--"
        bus2 = departs[1] if len(departs) > 1 else "--"
        
        html = f"""
        <div class="layout">
            <div class="title">Bus 123</div>
            <div class="content">
                <div class="item">
                    <span class="label">Vers</span>
                    <span class="value">Mairie d'Issy</span>
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
            <div class="footer">IDFM GPS</div>
        </div>
        """
        return jsonify({"markup": html})

    except Exception as e:
        return jsonify({"markup": f"Erreur code: {str(e)}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
