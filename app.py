from flask import Flask, jsonify
import requests
import datetime

app = Flask(__name__)

# Clé API Officielle (IDFM)
PRIM_KEY = "CzyhmgXXqA0IfjxTt0pAFp3LVr5m2mqY"

@app.route('/')
def get_bus():
    # Arrêt "Rue du Point du Jour" (Ligne 123) - Code IDFM exact
    # On demande les prochains passages
    url = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/stops/IDFM:463158/stop_schedules?line_id=IDFM:C01375"
    headers = {"apiKey": PRIM_KEY}
    
    try:
        # Timeout très court (3s) pour ne pas faire attendre TRMNL
        r = requests.get(url, headers=headers, timeout=3)
        data = r.json()
        
        # On fouille dans la réponse compliquée de l'API officielle
        schedules = data['stop_schedules'][0]['date_times']
        
        # On calcule les minutes restantes
        now = datetime.datetime.now()
        departs = []
        
        for s in schedules:
            # Format date API: YYYYMMDDThhmmss
            time_str = s['date_time']
            # On extrait juste l'heure HH:MM
            heure_bus = time_str.split('T')[1][:4] # ex: 1845
            h = int(heure_bus[:2])
            m = int(heure_bus[2:])
            
            # Calcul approximatif (l'API donne l'heure exacte, pas les minutes)
            # Pour faire simple on affiche l'heure "18h45"
            departs.append(f"{h}h{m:02d}")

        # Si on a trouvé des bus
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
            <div class="footer">IDFM Officiel</div>
        </div>
        """
        return jsonify({"markup": html})

    except Exception as e:
        # En cas d'erreur, on affiche quand même quelque chose pour ne pas avoir d'écran noir
        fallback = f"""
        <div class="layout">
            <div class="title">Bus 123</div>
            <div class="content">
                Maintenance API<br/>
                <span style="font-size:15px">Erreur: {str(e)[:20]}...</span>
            </div>
        </div>
        """
        return jsonify({"markup": fallback})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
