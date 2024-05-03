from datetime import datetime
import tkinter, tkintermapview, math, requests


def get_geojson(url):
    response = requests.get(url)
    if response.status_code == 200: #On récupère la réponse get
        return response.json() #On retourne un json
    else:
        print(f"Erreur pour charger les données de {url}") #Si on arrive pas à récupérer alors msg d'erreur
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

def callback_label(label):
    label['text'] = label.data

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

# Listes pour stocker des informations nécessaire à l'affichage
chemins_info = []
closest_stop_lines = []
stop_ids = []
correspondances_lignes = []
horaire_info = []

closest_stop = None
min_distance = float('inf')

# Traitement des relations entre tronçons et chemins
for feature in response_relation_troncon_chemin["features"]:
    rs_sv_chem_l = feature['properties']['rs_sv_chem_l']
    rs_sv_tronc_l = feature['properties']['rs_sv_tronc_l']
    if rs_sv_chem_l not in relation_troncon_chemin_dict:
        relation_troncon_chemin_dict[rs_sv_chem_l] = []
    relation_troncon_chemin_dict[rs_sv_chem_l].append(rs_sv_tronc_l)


# Identification de l'arrêt de tram le plus proche
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
            # Inversion latitude, longitude
            stop_lat, stop_lon = stop_coords[1], stop_coords[0]

            # Calcul de distance pour trouver les arrêts les plus proches de notre position
            distance = haversine_distance(gplat, gplng, stop_lat, stop_lon)
            if distance < min_distance:
                min_distance = distance
                closest_stop = feature

arrivee_stop_troncons = []
closest_stop_troncons = []

# Traitement des horaires de tram non réalisés (pour avoir les prochains)
for feature in response_horaires["features"]:
    if feature['properties']['source'] == "SAEIV_TRAM" and feature['properties']['etat'] == "NON_REALISE":
        horaire_estime = feature['properties']['hor_estime']
        arret_p = feature['properties']['rs_sv_arret_p']
        if arret_p not in horaires_arrets_dict:
            horaires_arrets_dict[arret_p] = []
        horaires_arrets_dict[arret_p].append(horaire_estime)

# On trie les horaires pour récupérer uniquement l'horaire la plus proche
for arret, horaires in horaires_arrets_dict.items():
    horaires.sort()
    horaires_arrets_dict[arret] = horaires[0] if horaires else None

# On récupère les différents tronçons de départ et d'arrivée
for feature in response_troncon["features"]:
    # On récupère le tronçon d'arrivée et on l'ajoute à la liste
    if (feature['properties']['vehicule'] == "TRAM"
    and arrets_dict.get(feature['properties']['rg_sv_arret_p_na']) == stop['properties']['libelle']):
        troncon_arrivee_gid = feature['properties']['gid']
        arrivee_stop_troncons.append(troncon_arrivee_gid)

# On récupère le/les tronçons les plus proches de notre position
    if (feature['properties']['vehicule'] == "TRAM"
    and arrets_dict.get(feature['properties']['rg_sv_arret_p_nd']) == closest_stop['properties']['libelle']):
        troncon_gid = feature['properties']['gid']
        # On récupère le tronçon de départ et on l'ajoute à la liste
        closest_stop_troncons.append(troncon_gid)

# On récupère les données de tous les tronçons ainsi que les coordonnées pour l'affichage
    if feature['properties']['vehicule'] == "TRAM":
        troncon_gid = feature['properties']['gid']
        depart_gid = feature['properties']['rg_sv_arret_p_nd']
        arrivee_gid = feature['properties']['rg_sv_arret_p_na']
        ligne_arret_libelle_depart = arrets_dict.get(depart_gid, "Arrêt inconnu")
        ligne_arret_libelle_arrivee = arrets_dict.get(arrivee_gid, "Arrêt inconnu")
        horaire_arret = horaires_arrets_dict.get(depart_gid)
        troncon_geoshape = [(point[1], point[0]) for point in feature['geometry']['coordinates']]

        troncon_dict[troncon_gid] = {
            "depart": ligne_arret_libelle_depart,
            "arrivee": ligne_arret_libelle_arrivee,
            "depart_gid": depart_gid,
            "arrivee_gid": arrivee_gid,
            "horaire": horaire_arret,
            "geoshape": troncon_geoshape
        }

# On récupère les différentes lignes et on crée un dictionnaire pour attacher chaque identifiant d'une ligne à la ligne de tram correspondante
for feature in response_lignes["features"]:
    if feature['properties']['vehicule'] == "TRAM":
        ligne_gid = feature['properties']['gid']
        ligne_libelle = feature['properties']['libelle']
        if ligne_libelle not in lignes_dict:
            lignes_dict[ligne_gid] = []
        lignes_dict[ligne_gid].append(ligne_libelle)


# On récupère les informations des chemins
for feature in response_chemins["features"]:
    if (feature['properties']['vehicule'] == "TRAM" 
    and feature['properties']['principal'] == True):
        # Partie ci-dessous nécessaire pour récupérer la ligne correspondante la plus proche en fonction de l'arrêt
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

# On trie pour afficher par ID de chemin croissant
chemins_info_sorted_gid = sorted(chemins_info, key=lambda x: x['chemin_gid'])


# Détermination des arrêts de changement et affichage des chemins correspondants
arret_tram_depart, arret_tram_arrivee = set(), set()

# Collecte des arrêts de départ et d'arrivée pour chaque tronçon
for chemin_info in chemins_info_sorted_gid:
    troncon_found = False
    troncon_mene_au_changement = False
    troncon_part_de_changement = False

    # On parcourt tous les tronçons et on vérifie si un des tronçons fait partie de ceux les plus proches    
    for troncon_gid in chemin_info['troncon']:
        if troncon_gid in closest_stop_troncons:
            troncon_found = True
    
    # Si troncon_found alors on l'ajoute à notre liste d'arrêt de départ
        if troncon_found:
            troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
            arret_tram_depart.add(troncon_info['depart'])
    
    # Si le tronçon est dans la liste du tronçon d'arrivée, on arrête
        if troncon_gid in arrivee_stop_troncons:
            break
    
    # Vérifier si le chemin contient le tronçon d'arrivée avant de commencer à afficher quoi que ce soit
    if any(troncon_gid in arrivee_stop_troncons for troncon_gid in chemin_info['troncon']):
        for troncon_gid in chemin_info['troncon']:
            troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
            arret_tram_arrivee.add(troncon_info['depart'])
            
# On repère les correspondances
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
        
        # On vérifie si le tronçon mène à l'arrêt de changement puis s'il part de l'arrêt de changement
        if troncon_found:
            troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
            if troncon_info['arrivee'] == arret_changement:
                troncon_mene_au_changement = True
            if troncon_info['depart'] == arret_changement:
                troncon_part_de_changement = True

    # Si une des 2 conditions validés, on ajoute ce chemin comme validé à la liste
    if troncon_mene_au_changement or troncon_part_de_changement:
        chemins_valides.append(chemin_info)


root_tk = tkinter.Tk()
root_tk.geometry(f"{1000}x{1000}")
map_widget = tkintermapview.TkinterMapView(root_tk, width=900, height=900, corner_radius=5);
map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
label = tkinter.Label(root_tk)
label.place(x=700, y=10)

colors = {'Tram A': 'red', 'Tram B': 'blue', 'Tram C': 'green', 'Tram D': 'purple'}


# On parcourt la liste des chemins valides
for chemin_info in chemins_valides:
    troncon_found = False
    first_iteration = True # Nécessaire pour afficher l'horaire de départ d'un seul tram

    for troncon_gid in chemin_info['troncon']:
        if troncon_gid in closest_stop_troncons:
            troncon_found = True
            print(f"{chemin_info['chemin_libelle']}: Ligne {chemin_info['ligne_libelle']}") # Affichage du libellé du chemin et de la ligne correspondante
        if troncon_found:
            troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
            # Print troncon sur la map
            map_widget.set_path(troncon_info['geoshape'], color=colors[chemin_info['ligne_libelle'][0]], data=chemin_info['ligne_libelle'][0], command=callback_label)
            if first_iteration:
                current_time = datetime.now()
                horaire = datetime.fromisoformat(troncon_info['horaire']).replace(tzinfo=None)
                time_diff = round((horaire - current_time).total_seconds() // 60) # Permet de récupérer le temps en minutes dans lequel le tram va partir
                map_widget.set_marker(troncon_info['geoshape'][0][0], troncon_info['geoshape'][0][1], data=troncon_info['depart'], command=callback_label)
                print(f"\033[1m Dans {time_diff} minutes, Départ {troncon_info['depart']} -> Arrivée {troncon_info['arrivee']} \033[0m")
                first_iteration = False # On passe à false pour ne plus afficher le temps dans lequel part les autres tram, uniquement celui le plus proche de nous nous intéresse
            else:
                # Affichage de l'itinéraire jusqu'au changement d'arrêt
                print(f"Départ {troncon_info['depart']} -> Arrivée {troncon_info['arrivee']}")


            if arret_changement == troncon_info['arrivee']:
                for chemin_info in [chemin_info for chemin_info in chemins_info_sorted_gid if any(troncon_gid in arrivee_stop_troncons for troncon_gid in chemin_info['troncon'])][:1]:
                    start_printing = False # Flag pour savoir si on doit afficher ou non le trajet
                    for troncon_gid in chemin_info['troncon']:
                        troncon_info = troncon_dict.get(troncon_gid, {"depart": "Départ inconnu", "arrivee": "Arrivée inconnue"})
                        # Commencer à afficher à partir de l'arrêt de changement
                        if troncon_info['depart'] == arret_changement or start_printing:
                            if not start_printing:
                                print(f"\033[1m Changement d'arrêt : {arret_changement}, Ligne {chemin_info['ligne_libelle']} \033[0m")
                                map_widget.set_marker(troncon_info['geoshape'][0][0], troncon_info['geoshape'][0][1],data=arret_changement, command=callback_label)
                            start_printing = True
                            map_widget.set_path(troncon_info['geoshape'], color=colors[chemin_info['ligne_libelle'][0]], data=chemin_info['ligne_libelle'][0], command=callback_label)
                            print(f"Départ {troncon_info['depart']} -> Arrivée {troncon_info['arrivee']}")
                        if troncon_gid in arrivee_stop_troncons and start_printing:
                            map_widget.set_marker(troncon_info['geoshape'][-1][0], troncon_info['geoshape'][-1][1], data=troncon_info['arrivee'], command=callback_label)
                            break
        if troncon_gid in arrivee_stop_troncons:
            break

map_widget.set_position(44.86596236872216, -0.5757273765736807)
map_widget.set_zoom(18)
root_tk.mainloop()
