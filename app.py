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
        
        # Secours
        if not schedules and len(data['stop_schedules']) > 0:
            schedules = data['stop_schedules'][0]['date_times']

        # 4 horaires
        departs = []
        for s in schedules:
            dt = datetime.strptime(s['date_time'], "%Y%m%dT%H%M%S")
            departs.append(dt.strftime("%H:%M"))
            if len(departs) == 4:
                break

        while len(departs) < 4:
            departs.append("--:--")

        bus1 = departs[0]
        bus2 = departs[1]
        bus3 = departs[2]
        bus4 = departs[3]
        
        # Icône Bus
        bus_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2C8 2 4 2.5 4 6v9.5c0 .95.38 1.81 1 2.44V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-2.06c.62-.63 1-1.49 1-2.44V6c0-3.5-3.58-4-8-4zm5.66 2.99H6.34C6.89 4.46 8.31 4 12 4s5.11.46 5.66 .99zm.34 2V10H6V6.99h12zm-9 10c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm8 0c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/></svg>"""
        
        html = f"""
        <div class="layout" style="text-align: center; font-family: sans-serif; display: flex; flex-direction: column; height: 100%; align-items: center; justify-content: center;">
            
            <div class="header" style="border-bottom: 2px solid black; padding-bottom: 5px; margin-bottom: 5px; width: 90%;">
                <div style="display: flex; align-items: center; justify-content: center;">
                    <span style="margin-right: 6px; margin-top: 3px;">{bus_icon}</span>
                    <span style="font-size: 22px; font-weight: bold;">Bus 123</span>
                </div>
                <div style="font-size: 11px; margin-top: 2px; text-transform: uppercase; letter-spacing: 1px;">
                    Rue du Point du Jour
                </div>
            </div>

            <div style="font-size: 13px; margin-bottom: 10px; font-style: italic; opacity: 0.8;">
                Vers {direction_label}
            </div>

            <div style="font-size: 65px; font-weight: 800; line-height: 1; margin: 10px 0 20px 0; letter-spacing: -3px;">
                {bus1}
            </div>

            <div style="border-top: 1px dotted #aaa; width: 60%; margin-bottom: 25px;"></div>

            <div style="display: flex; justify-content: center; gap: 20px;">
                
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <span style="font-size: 10px; text-transform: uppercase; opacity: 0.6; margin-bottom: 2px;">Suivant</span>
                    <strong style="font-size: 30px; line-height: 1;">{bus2}</strong>
                </div>

                <div style="display: flex; flex-direction: column; align-items: center;">
                    <span style="font-size: 10px; text-transform: uppercase; opacity: 0.6; margin-bottom: 2px;">Ensuite</span>
                    <strong style="font-size: 30px; line-height: 1;">{bus3}</strong>
                </div>

                <div style="display: flex; flex-direction: column; align-items: center;">
                    <span style="font-size: 10px; text-transform: uppercase; opacity: 0.6; margin-bottom: 2px;">+ Tard</span>
                    <strong style="font-size: 30px; line-height: 1;">{bus4}</strong>
                </div>

            </div>
        </div>
        """
        return jsonify({"markup": html})

    except Exception as e:
        return jsonify({"markup": f"Erreur: {str(e)[:20]}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
