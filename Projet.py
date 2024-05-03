from datetime import datetime
import tkinter, tkintermapview, math, requests

def get_geojson(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to load data from {url}")
        return None
    
def haversine_distance(lat1, lon1, lat2, lon2):
    # Convertir les degrés en radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Différence des coordonnées
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Formule de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Rayon de la Terre en kilomètres
    r = 6371
    
    return c * r


# Position actuelle
gplat = 44.866072
gplng = -0.576524

# URLs des données GeoJSON
arrets_transports_path = "https://data.bordeaux-metropole.fr/geojson?key=5MCBG792IH&typename=sv_arret_p"
chemins_transports_path = "https://data.bordeaux-metropole.fr/geojson?key=5MCBG792IH&typename=sv_chem_l"
lignes_transports_path = "https://data.bordeaux-metropole.fr/geojson?key=5MCBG792IH&typename=sv_ligne_a"
troncon_transports_path = "https://data.bordeaux-metropole.fr/geojson?key=5MCBG792IH&typename=sv_tronc_l"
horaires_arrets_path = "https://data.bordeaux-metropole.fr/geojson?key=5MCBG792IH&typename=sv_horai_a"
relation_troncon_chemin_path = "https://data.bordeaux-metropole.fr/geojson/relations/SV_TRONC_L/SV_CHEM_L?key=5MCBG792IH"



response_arrets = get_geojson(arrets_transports_path)
response_chemins = get_geojson(chemins_transports_path)
response_lignes = get_geojson(lignes_transports_path)
response_troncon = get_geojson(troncon_transports_path)
response_horaires = get_geojson(horaires_arrets_path)
response_relation_troncon_chemin = get_geojson(relation_troncon_chemin_path)

# Dictionnaire pour stocker les libellés des lignes de tram
lignes_dict = {}
arrets_dict = {}
troncon_dict = {}
horaires_arrets_dict = {}

relation_troncon_chemin_dict = {}
chemins_info = []
closest_stop_lines = []
stop_ids = []
correspondances_lignes = []
horaire_info = []

closest_stop = None
min_distance = float('inf')

for feature in response_relation_troncon_chemin["features"]:
    rs_sv_chem_l = feature['properties']['rs_sv_chem_l']
    rs_sv_tronc_l = feature['properties']['rs_sv_tronc_l']
    if rs_sv_chem_l not in relation_troncon_chemin_dict:
        relation_troncon_chemin_dict[rs_sv_chem_l] = []
    relation_troncon_chemin_dict[rs_sv_chem_l].append(rs_sv_tronc_l)

for feature in response_arrets["features"]:
    if feature['properties']['groupe'] == "T_AEROP":
        stop_id = feature['properties']['gid']
        stop_ids.append(stop_id)
        stop = feature

    if (feature['geometry'] is not None and feature['geometry']['coordinates']
            and feature['properties']['vehicule'] == 'TRAM'):
            arret_gid = feature['properties']['gid']
            arret_libelle = feature['properties']['libelle']
            arrets_dict[arret_gid] = arret_libelle
            stop_coords = feature['geometry']['coordinates']
            stop_lat = stop_coords[1]
            stop_lon = stop_coords[0]
    
            distance = haversine_distance(gplat, gplng, stop_lat, stop_lon)
            if distance < min_distance:
                min_distance = distance
                closest_stop = feature

arrivee_stop_troncons = []
closest_stop_troncons = []

for feature in response_horaires["features"]:
    if feature['properties']['source'] == "SAEIV_TRAM" and feature['properties']['etat'] == "NON_REALISE":
        horaire_estime = feature['properties']['hor_estime']
        arret_p = feature['properties']['rs_sv_arret_p']
        if arret_p not in horaires_arrets_dict:
            horaires_arrets_dict[arret_p] = []
        horaires_arrets_dict[arret_p].append(horaire_estime)

for arret, horaires in horaires_arrets_dict.items():
    horaires.sort()
    horaires_arrets_dict[arret] = horaires[0] if horaires else None

for feature in response_troncon["features"]:
    if (feature['properties']['vehicule'] == "TRAM"
    and arrets_dict.get(feature['properties']['rg_sv_arret_p_na']) == stop['properties']['libelle']):
        troncon_arrivee_gid = feature['properties']['gid']
        arrivee_stop_troncons.append(troncon_arrivee_gid)

    if (feature['properties']['vehicule'] == "TRAM"
    and arrets_dict.get(feature['properties']['rg_sv_arret_p_nd']) == closest_stop['properties']['libelle']):
        troncon_gid = feature['properties']['gid']
        closest_stop_troncons.append(troncon_gid)

    if feature['properties']['vehicule'] == "TRAM":
        troncon_gid = feature['properties']['gid']
        depart_gid = feature['properties']['rg_sv_arret_p_nd']
        arrivee_gid = feature['properties']['rg_sv_arret_p_na']
        ligne_arret_libelle_depart = arrets_dict.get(depart_gid, "Arrêt inconnu")
        ligne_arret_libelle_arrivee = arrets_dict.get(arrivee_gid, "Arrêt inconnu")
        horaire_arret = horaires_arrets_dict.get(depart_gid)
        troncon_geoshape = feature['geometry']

        troncon_dict[troncon_gid] = {
            "depart": ligne_arret_libelle_depart,
            "arrivee": ligne_arret_libelle_arrivee,
            "depart_gid": depart_gid,
            "arrivee_gid": arrivee_gid,
            "horaire": horaire_arret,
            "geoshape": troncon_geoshape
        }

for feature in response_lignes["features"]:
    if feature['properties']['vehicule'] == "TRAM":
        ligne_gid = feature['properties']['gid']
        ligne_libelle = feature['properties']['libelle']
        if ligne_libelle not in lignes_dict:
            lignes_dict[ligne_gid] = []
        lignes_dict[ligne_gid].append(ligne_libelle)

for feature in response_chemins["features"]:
    if (feature['properties']['vehicule'] == "TRAM" 
    and feature['properties']['principal'] == True):
        if closest_stop and feature['properties']['rg_sv_arret_p_nd'] == closest_stop['properties']['gid']:
            closest_stop_lines.append(lignes_dict.get(feature['rs_sv_ligne_a'], "Ligne inconnue"))
        chemin_gid = feature['properties']['gid']
        chemin_ligne = feature['properties']['rs_sv_ligne_a']
        chemin_libelle = feature['properties']['libelle']
        chemin_rg_sv_arret_p_nd = feature['properties']['rg_sv_arret_p_nd']
        chemin_rg_sv_arret_p_na = feature['properties']['rg_sv_arret_p_na']
        ligne_troncon = relation_troncon_chemin_dict.get(chemin_gid)
        ligne_libelle = lignes_dict.get(chemin_ligne)

        chemins_info.append({
            "chemin_gid": chemin_gid,
            "chemin_libelle": chemin_libelle,
            "ligne_libelle": ligne_libelle,
            "troncon": ligne_troncon
        })

chemins_info_sorted_gid = sorted(chemins_info, key=lambda x: x['chemin_gid'])
arret_tram_depart, arret_tram_arrivee = set(), set()

# Collecte des arrêts de départ et d'arrivée pour chaque tronçon pertinent
for chemin_info in chemins_info_sorted_gid:
    troncon_found = False
    troncon_mene_au_changement = False
    troncon_part_de_changement = False
    
    for troncon_gid in chemin_info['troncon']:
        if troncon_gid in closest_stop_troncons:
            troncon_found = True

        if troncon_found:
            troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
            arret_tram_depart.add(troncon_info['depart'])
            
        if troncon_gid in arrivee_stop_troncons:
            break
    
    # Vérifier si le chemin contient le tronçon d'arrivée avant de commencer à afficher quoi que ce soit
    if any(troncon_gid in arrivee_stop_troncons for troncon_gid in chemin_info['troncon']):
        #print(f"{chemin_info['chemin_libelle']}: Ligne {chemin_info['ligne_libelle']}")
        for troncon_gid in chemin_info['troncon']:
            troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
            arret_tram_arrivee.add(troncon_info['depart'])
            
arrets_communs = arret_tram_depart.intersection(arret_tram_arrivee)
arret_changement = next(iter(arrets_communs), None) 
chemins_valides = []

for chemin_info in chemins_info_sorted_gid:
    troncon_mene_au_changement = False
    troncon_part_de_changement = False
    troncon_found = False

    for troncon_gid in chemin_info['troncon']:
        if troncon_gid in closest_stop_troncons:
            troncon_found = True
        
        if troncon_found:
            troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
            if troncon_info['arrivee'] == arret_changement:
                troncon_mene_au_changement = True
            if troncon_info['depart'] == arret_changement:
                troncon_part_de_changement = True

    if troncon_mene_au_changement or troncon_part_de_changement:
        chemins_valides.append(chemin_info)



for chemin_info in chemins_valides:
    troncon_found = False
    first_iteration = True

    for troncon_gid in chemin_info['troncon']:
        if troncon_gid in closest_stop_troncons:
            troncon_found = True
            print(f"{chemin_info['chemin_libelle']}: Ligne {chemin_info['ligne_libelle']}")
        if troncon_found:
            troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
            if first_iteration:
                current_time = datetime.now()
                horaire = datetime.fromisoformat(troncon_info['horaire']).replace(tzinfo=None)
                time_diff = round((horaire - current_time).total_seconds() // 60)
                print(f"\033[1m Dans {time_diff} minutes, Départ {troncon_info['depart']} -> Arrivée {troncon_info['arrivee']} \033[0m")
                first_iteration = False
            else:
                print(f"Départ {troncon_info['depart']} -> Arrivée {troncon_info['arrivee']}")

            if arret_changement == troncon_info['arrivee']:
                for chemin_info in [chemin_info for chemin_info in chemins_info_sorted_gid if any(troncon_gid in arrivee_stop_troncons for troncon_gid in chemin_info['troncon'])][:1]:
                    start_printing = False 
                    for troncon_gid in chemin_info['troncon']:
                        troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
                        # Commencer à imprimer à partir de l'arrêt de changement
                        if troncon_info['depart'] == arret_changement or start_printing:
                            if not start_printing:
                                print(f"\033[1m Changement d'arrêt : {arret_changement}, Ligne {chemin_info['ligne_libelle']} \033[0m")
                            start_printing = True
                            print(f"Départ {troncon_info['depart']} -> Arrivée {troncon_info['arrivee']}")
                        if troncon_gid in arrivee_stop_troncons and start_printing:
                            break
        if troncon_gid in arrivee_stop_troncons:
            break


root_tk = tkinter.Tk()
root_tk.geometry(f"{1000}x{1000}")
map_widget = tkintermapview.TkinterMapView(root_tk, width=900, height=900, corner_radius=5);
map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
map_widget.set_position(44.86596236872216, -0.5757273765736807)
map_widget.set_zoom(18)
root_tk.mainloop()