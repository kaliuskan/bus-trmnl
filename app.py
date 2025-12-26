from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Clé API IDFM
PRIM_KEY = "CzyhmgXXqA0IfjxTt0pAFp3LVr5m2mqY"

@app.route('/')
def get_bus():
    # 1. On cherche les horaires GPS
    url = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/coords/2.2527;48.8328/stop_schedules?line_id=line:IDFM:C01375"
    headers = {"apiKey": PRIM_KEY}
    
    try:
        r = requests.get(url, headers=headers, timeout=6)
        data = r.json()
        
        if not data.get('stop_schedules'):
             return jsonify({"markup": "⚠️ Pas d'horaires"})

        # 2. FILTRE INTELLIGENT : On cherche la direction "Porte d'Auteuil"
        # L'API peut renvoyer les deux sens, on veut le bon.
        schedules = []
        direction_label = "Porte d'Auteuil" # Label par défaut
        
        for schedule_group in data['stop_schedules']:
            # On regarde la direction écrite dans l'API
            direction_api = schedule_group.get('display_informations', {}).get('direction', '').lower()
            
            # Si ça parle d'Auteuil, c'est le bon bus !
            if "auteuil" in direction_api:
                schedules = schedule_group['date_times']
                break
        
        # Si on n'a rien trouvé avec le filtre, on prend le premier par défaut (secours)
        if not schedules and len(data['stop_schedules']) > 0:
            schedules = data['stop_schedules'][0]['date_times']

        # 3. Mise en forme des heures
        departs = []
        for s in schedules:
            dt = datetime.strptime(s['date_time'], "%Y%m%dT%H%M%S")
            departs.append(dt.strftime("%H:%M"))

        bus1 = departs[0] if len(departs) > 0 else "--:--"
        bus2 = departs[1] if len(departs) > 1 else "--:--"
        
        # Icône Bus
        bus_icon = """<svg xmlns="http://www.w3.org/2000/svg" height="26" viewBox="0 -960 960 960" width="26" fill="currentColor"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h60v-320H200v320Zm140 0h280v-320H340v320Zm360 0h60v-320h-60v320ZM200-600h560v-160H200v160Zm0 0v-160 160Zm280 240q-25 0-42.5-17.5T420-420q0-25 17.5-42.5T480-480q25 0 42.5 17.5T540-420q0 25-17.5 42.5T480-360Z"/></svg>"""
        
        html = f"""
        <div class="layout" style="text-align: center;">
            <div class="title" style="display: flex; align-items: center; justify-content: center; margin-bottom: 5px;">
                <span style="margin-right: 8px;">{bus_icon}</span>
                <span>Bus 123</span>
            </div>
            
            <div class="content" style="background-color: white; border-radius: 8px; padding: 5px;">
                <div class="item" style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">
                    Vers {direction_label}
                </div>
                
                <div class="item" style="margin: 5px 0;">
                    <span class="value" style="font-size: 45px; font-weight:bold; letter-spacing: -2px; line-height: 1;">{bus1}</span>
                </div>
                
                <div style="border-top: 1px solid black; margin: 5px auto; width: 30%;"></div>
                
                <div class="item" style="font-size: 18px;">
                    <span class="label" style="opacity: 0.6; font-size: 14px;">Suivant:</span>
                    <span class="value">{bus2}</span>
                </div>
            </div>
        </div>
        """
        return jsonify({"markup": html})

    except Exception as e:
        return jsonify({"markup": f"Erreur: {str(e)[:20]}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
