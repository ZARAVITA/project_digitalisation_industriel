# 🔧 Application de Gestion des Rapports de Maintenance

Application professionnelle Streamlit pour le suivi des équipements industriels et de leurs observations de maintenance.

## 📁 Structure du projet

```
maintenance-app/
│
├── app.py                          # Point d'entrée principal
├── requirements.txt                # Dépendances Python
│
├── data/                           # Répertoire données (créé automatiquement)
│   ├── equipements.xlsx            # Référentiel équipements
│   └── observations.csv            # Historique observations
|   ├── data_manager_supabase.py    
│
├── data/
│   └── data_manager.py             # Couche d'accès données
│
└── ui/                             # Modules d'interface
    ├── equipements.py              # Onglet Équipements
    ├── observations.py             # Onglet Observations
    ├── telechargements.py          # Onglet Téléchargements
    └── suppressions.py             # Onglet Suppressions
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Étapes

1. **Cloner ou créer le projet**
```bash
mkdir maintenance-app
cd maintenance-app
```

2. **Créer l'environnement virtuel (recommandé)**
```bash
python -m venv venv

# Activation
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Créer la structure des dossiers**
```bash
mkdir data
mkdir data
mkdir ui
```

5. **Copier les fichiers Python** dans leur emplacement respectif

## ▶️ Lancement

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

## 📖 Guide d'utilisation

### 1️⃣ Onglet Équipements

**Objectif** : Visualiser le référentiel des équipements

**Fonctionnalités** :
- Tableau de tous les équipements
- Filtrage par département(s)
- Export Excel (filtré ou complet)
- Statistiques par département

**Cas d'usage** :
- Consulter la liste des équipements d'un département
- Exporter le référentiel pour un rapport
- Vérifier le nombre d'équipements par zone

### 2️⃣ Onglet Observations

**Objectif** : Saisir et consulter l'historique

**Bloc 1 - Nouvelle observation** :
1. Sélectionner le département
2. Choisir l'équipement (liste filtrée)
3. Définir la date
4. Remplir les champs (observation requise)
5. Indiquer le nom de l'analyste (requis)
6. Cliquer sur "Enregistrer"

**Bloc 2 - Historique** :
- Affichage par défaut : 5 observations les plus récentes
- Filtres disponibles :
  - Département(s)
  - Équipement(s)
  - Période (date début/fin)
- Tableau complet avec tous les détails

### 3️⃣ Onglet Téléchargements

**Objectif** : Générer des exports Excel filtrés

**Rapport d'observations** :
1. Appliquer les filtres souhaités
2. Vérifier le nombre d'observations sélectionnées
3. Cliquer sur "Télécharger"
4. Le fichier contient : département, ID, date, observation, recommandation, travaux, analyste

**Liste des équipements** :
1. Filtrer par département si besoin
2. Télécharger la liste

**Nom des fichiers** : Horodatage automatique pour éviter les écrasements

### 4️⃣ Onglet Suppressions

**⚠️ Zone critique - Utilisation contrôlée**

**Supprimer une observation** :
1. Sélectionner l'équipement
2. Indiquer la date exacte
3. Cliquer sur "Supprimer"
4. Confirmer l'action

**Supprimer un équipement** :
1. Sélectionner l'équipement
2. ⚠️ ATTENTION : Toutes les observations associées seront supprimées
3. Confirmer la suppression définitive

**Bonnes pratiques** :
- Exportez vos données avant toute suppression importante
- Vérifiez toujours les informations affichées
- Les suppressions sont irréversibles

## 🏗️ Architecture technique

### Séparation des responsabilités

**`app.py`** : Point d'entrée, navigation
**`data/data_manager.py`** : Gestion données (CRUD)
**`ui/*.py`** : Modules d'interface par onglet

### Choix techniques

- **Stockage** : Excel + CSV (migration Supabase prévue)
- **Framework** : Streamlit (UX rapide)
- **Données** : Pandas (manipulation)

### Points de migration Supabase

Les fonctions dans `data_manager.py` sont conçues pour être facilement migrées :

```python
# Actuellement : CSV/Excel
def charger_observations():
    return pd.read_csv(OBSERVATIONS_FILE)

# Future migration :
def charger_observations():
    return supabase.table('observations').select('*').execute()
```

**Fonctions à migrer** :
- `charger_equipements()`
- `charger_observations()`
- `sauvegarder_observation()`
- `supprimer_observation()`
- `supprimer_equipement()`

## 🎨 Conventions de code

### Style
- Noms de fonctions : `snake_case`
- Commentaires : Français (contexte métier)
- Docstrings : Format Google

### Organisation
- Un onglet = un fichier dans `ui/`
- Logique métier dans `data_manager.py`
- UI pure dans les modules `ui/`

## 🔧 Maintenance

### Ajouter un équipement manuellement

Éditer `data/equipements.xlsx` :
```
id_equipement    | departement
-----------------+------------------
NOUVEAU-ID-123   | NOM_DEPARTEMENT
```

### Sauvegarder les données

Copiez régulièrement :
```bash
cp data/equipements.xlsx backups/equipements_YYYYMMDD.xlsx
cp data/observations.csv backups/observations_YYYYMMDD.csv
```

### Réinitialiser les données

Supprimez le dossier `data/` et relancez l'application. Les fichiers seront recréés avec les données exemples.

## 🐛 Dépannage

**Erreur "Colonnes manquantes"**
- Vérifiez la structure des fichiers Excel/CSV
- Les colonnes doivent correspondre exactement aux schémas définis

**L'application ne démarre pas**
- Vérifiez que toutes les dépendances sont installées
- Assurez-vous que la structure des dossiers est correcte

**Données non sauvegardées**
- Vérifiez les permissions d'écriture dans le dossier `data/`

## 📝 Évolutions futures

- [ ] Migration vers Supabase (base de données)
- [ ] Authentification utilisateurs
- [ ] Historique des modifications
- [ ] Pièces jointes (photos)
- [ ] Notifications automatiques
- [ ] Tableau de bord analytique

## 👥 Support

Pour toute question ou problème :
1. Vérifiez ce README
2. Consultez les messages d'erreur dans la console
3. Contactez l'équipe technique

---

**Version** : 2.0 (Refactorisée)  
**Dernière mise à jour** : Janvier 2025