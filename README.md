# Traitement des horaires de tramway de Bordeaux

## Description
Ce script est conçu pour interagir avec l'API GeoJSON de l'atelier OPENDATA de Bordeaux Métropole afin de récupérer et traiter les données des différentes lignes de tramway, incluant les arrêts, les itinéraires, les tronçons et les horaires. Il identifie les arrêts de tram les plus proches d'une position GPS donnée, recueille les premiers horaires de passage estimés pour chaque arrêt, et traite les informations des itinéraires et tronçons de tramway pour une analyse ou une visualisation ultérieure.

## Fonctionnalités
- **Identification de l'arrêt le plus proche** : Détermine l'arrêt de tram le plus proche d'une position GPS donnée.
- **Traitement des horaires** : Récupère le premier horaire estimé pour les arrêts de tram.
- **Analyse des itinéraires et tronçons** : Collecte et traite les données des itinéraires et tronçons de tramway pour identifier les connexions et parcours pertinents.

## Sources de données
Le script utilise plusieurs points de terminaison GeoJSON fournis par Bordeaux Métropole pour collecter les données :
- Arrêts (`sv_arret_p`)
- Itinéraires (`sv_chem_l`)
- Lignes (`sv_ligne_a`)
- Tronçons (`sv_tronc_l`)
- Horaires (`sv_horai_a`)
- Relations Itinéraire-Tronçon (`relations/SV_TRONC_L/SV_CHEM_L`)

## Configuration
### Prérequis
- Python 3.x
- Accès à Internet pour récupérer les données depuis l'API de Bordeaux Métropole
- Clé API pour interroger l'API

### Bibliothèques
Assurez-vous d'avoir installé les bibliothèques Python suivantes :
```bash
pip install -r requirements.txt
```

## Utilisation
1. **Configurer les coordonnées GPS** : Définissez les variables `gplat` et `gplng` avec votre position GPS actuelle. Une amélioration possible, est de récupérer depuis une carte, les coordonnées d'un marqueur.

2. **Exécuter le script** : Exécutez le script pour traiter et afficher les données des tramways.
   ```bash
   python Projet.py
   ```

## Fonctions principales
- `get_geojson(url)`: Récupère les données depuis l'endpoint API GeoJSON spécifié.
- `haversine_distance(lat1, lon1, lat2, lon2)`: Calcule la distance entre deux coordonnées GPS.

## Exemples de sorties
- Liste des arrêts de tram les plus proches avec l'horaire de passage en minutes "Dans X minutes" de l'arrêt de tram le plus proche.
- Détails des itinéraires de tram partant de l'arrêt le plus proche.

![Exemple de sortie en brut](image.png)


## Fichiers
- `Projet.py`: Script principal contenant toute la logique de traitement.

## Avertissement
Ce script est à des fins éducatives uniquement. Les applications en temps réel peuvent nécessiter de gérer les mises à jour et les modifications fournies par le fournisseur d'API.

## Utilisation des données
Les données utilisées par ce script sont fournies par Bordeaux Métropole via son API GeoJSON. L'utilisation de ces données est soumise aux termes et conditions de Bordeaux Métropole. Les utilisateurs du script doivent également se conformer à ces termes et vérifier les conditions d'utilisation sur le [site officiel](https://opendata.bordeaux-metropole.fr/pages/accueil/) avant d'utiliser les données.

## Contributions
Les contributions au projet sont les bienvenues, mais les contributeurs doivent également s'assurer de respecter les droits d'auteur et les licences des bibliothèques ou des ressources tierces utilisées dans ce projet.