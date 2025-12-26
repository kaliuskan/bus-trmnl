from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Clé API IDFM
PRIM_KEY = "CzyhmgXXqA0IfjxTt0pAFp3LVr5m2mqY"

@app.route('/')
def get_bus():
    # Coordonnées GPS Rue du Point du Jour
    url = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/coords/2.2527;48.8328/stop_schedules?line_id=line:IDFM:C01375"
    headers = {"apiKey": PRIM_KEY}
    
    try:
        r = requests.get(url, headers=headers, timeout=6)
        data = r.json()
        
        if not data.get('stop_schedules'):
             return jsonify({"markup": "⚠️ Pas d'horaires"})

        # Filtre direction "Porte d'Auteuil"
        schedules = []
        direction_label = "Porte d'Auteuil"
        
        for schedule_group in data['stop_schedules']:
            direction_api = schedule_group.get('display_informations', {}).get('direction', '').lower()
            if "auteuil" in direction_api:
                schedules = schedule_group['date_times']
                break
        
        # Secours si filtre échoue
        if not schedules and len(data['stop_schedules']) > 0:
            schedules = data['stop_schedules'][0]['date_times']

        # On récupère les 3 prochains horaires
        departs = []
        for s in schedules:
            dt = datetime.strptime(s['date_time'], "%Y%m%dT%H%M%S")
            departs.append(dt.strftime("%H:%M"))
            if len(departs) == 3: # On s'arrête à 3 horaires
                break

        # Remplissage vide si moins de 3 bus
        while len(departs) < 3:
            departs.append("--:--")

        bus1 = departs[0]
        bus2 = departs[1]
        bus3 = departs[2]
        
        # Icône Bus
        bus_icon = """<svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="currentColor"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h60v-320H200v320Zm140 0h280v-320H340v320Zm360 0h60v-320h-60v320ZM200-600h560v-160H200v160Zm0 0v-160 160Zm280 240q-25 0-42.5-17.5T420-420q0-25 17.5-42.5T480-480q25 0 42.5 17.5T540-420q0 25-17.5 42.5T480-360Z"/></svg>"""
        
        html = f"""
        <div class="layout" style="text-align: center; font-family: sans-serif; display: flex; flex-direction: column; height: 100%;">
            
            <div class="header" style="border-bottom: 2px solid black; padding-bottom: 5px; margin-bottom: 5px;">
                <div style="display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold;">
                    <span style="margin-right: 8px; margin-top: 4px;">{bus_icon}</span>
                    <span>Ligne 123</span>
                </div>
                <div style="font-size: 12px; margin-top: 2px;">
                    Rue du Point du Jour
                </div>
            </div>

            <div style="font-size: 14px; margin-bottom: 5px;">
                Vers <strong>{direction_label}</strong>
            </div>

            <div style="font-size: 55px; font-weight: 800; line-height: 1; margin: 10px 0;">
                {bus1}
            </div>

            <div style="display: flex; justify-content: center; gap: 15px; font-size: 20px; border-top: 1px dotted #aaa; padding-top: 8px;">
                <div>
                    <span style="font-size: 12px; display: block; opacity: 0.6;">Suivant</span>
                    <strong>{bus2}</strong>
                </div>
                <div>
                    <span style="font-size: 12px; display: block; opacity: 0.6;">Après</span>
                    <strong>{bus3}</strong>
                </div>
            </div>

        </div>
        """
        return jsonify({"markup": html})

    except Exception as e:
        return jsonify({"markup": f"Erreur: {str(e)[:20]}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
