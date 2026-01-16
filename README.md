# 🔧 MVP Gestion des Rapports de Maintenance

Application web interne Streamlit pour digitaliser les rapports mensuels de maintenance des équipements industriels.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Internal-green.svg)]()

---

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Configuration](#-configuration)
- [Architecture technique](#-architecture-technique)
- [Évolutions futures](#-évolutions-futures)
- [Contribution](#-contribution)
- [Support](#-support)

---

## 🎯 Vue d'ensemble

### Contexte
Cette application remplace un processus manuel basé sur des fichiers Excel mensuels. Elle permet aux analystes techniques de :
- **Saisir** des observations et recommandations sur les équipements
- **Consulter** l'historique complet des interventions
- **Exporter** des rapports Excel professionnels

### Public cible
- Analystes techniques
- Responsables de maintenance
- Équipes d'inspection

### Périmètre MVP
- 20 équipements maximum
- Stockage fichier (CSV/Excel)
- Déploiement interne uniquement

---

## ✨ Fonctionnalités

### 1. Saisie des observations
- ✅ Sélection par département puis équipement (cascade)
- ✅ Champ date avec calendrier intégré
- ✅ Zones de texte pour observation et recommandation
- ✅ Identification de l'analyste
- ✅ Validation des champs obligatoires
- ✅ Sauvegarde persistante en CSV

### 2. Consultation de l'historique
- ✅ Tableau interactif de toutes les observations
- ✅ Filtres dynamiques par département
- ✅ Filtres dynamiques par équipement
- ✅ Tri automatique par date (plus récent en premier)
- ✅ Compteur d'observations affichées

### 3. Export Excel
- ✅ Génération d'un fichier Excel complet
- ✅ Fusion automatique des données équipements + observations
- ✅ Colonnes formatées en français
- ✅ Largeur des colonnes auto-ajustée
- ✅ Nom de fichier horodaté
- ✅ Téléchargement direct depuis l'interface

### 4. Gestion des données
- ✅ Chargement automatique depuis `equipements.xlsx`
- ✅ Données d'exemple créées au premier lancement
- ✅ Persistance dans `observations.csv`
- ✅ Validation de la structure des fichiers

---

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### Étapes d'installation

#### 1. Cloner ou télécharger le projet
```bash
git clone <url-du-repo>
cd rapport-maintenance-mvp
```

#### 2. Créer un environnement virtuel (recommandé)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Installer les dépendances
```bash
pip install streamlit pandas openpyxl
```

Ou via un fichier `requirements.txt` :
```bash
pip install -r requirements.txt
```

**Contenu du `requirements.txt` :**
```
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
```

---

## 💻 Utilisation

### Démarrage de l'application

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur par défaut sur :
```
http://localhost:8501
```

### Workflow typique

#### **Étape 1 : Saisir une observation**
1. Sélectionner le **département** concerné
2. Choisir l'**équipement** dans la liste filtrée
3. Sélectionner la **date** d'observation
4. Rédiger l'**observation** (obligatoire)
5. Rédiger la **recommandation** (optionnel mais conseillé)
6. Indiquer le nom de l'**analyste** (obligatoire)
7. Cliquer sur **Enregistrer**

#### **Étape 2 : Consulter l'historique**
1. Utiliser les filtres pour cibler un département ou équipement
2. Consulter le tableau interactif
3. Vérifier le compteur d'observations affichées

#### **Étape 3 : Exporter en Excel**
1. Descendre jusqu'à la section "Export Excel"
2. Cliquer sur **Télécharger Excel**
3. Le fichier est généré avec horodatage : `rapport_maintenance_YYYYMMDD_HHMMSS.xlsx`

---

## 📁 Structure du projet

```
rapport-maintenance-mvp/
│
├── app.py                      # Application Streamlit principale
├── README.md                   # Documentation (ce fichier)
├── requirements.txt            # Dépendances Python
│
└── data/                       # Répertoire de données (créé automatiquement)
    ├── equipements.xlsx        # Base des équipements
    └── observations.csv        # Historique des observations
```

### Description des fichiers

#### `app.py`
Fichier principal contenant :
- Configuration Streamlit
- Fonctions de chargement/sauvegarde des données
- Interface utilisateur
- Logique métier

#### `data/equipements.xlsx`
Structure :
```
| id_equipement | departement  |
|---------------|--------------|
| EQ001         | Production   |
| EQ002         | Production   |
| EQ003         | Logistique   |
```

#### `data/observations.csv`
Structure :
```
id_equipement,date,observation,recommandation,analyste
EQ001,2025-01-12,"Fuite détectée","Remplacer joint",Jean Dupont
```

---

## ⚙️ Configuration

### Personnaliser les équipements

#### Méthode 1 : Modifier le fichier Excel
1. Ouvrir `data/equipements.xlsx`
2. Respecter la structure des colonnes :
   - `id_equipement` : Identifiant unique (ex: EQ001)
   - `nom_equipement` : Nom descriptif
   - `departement` : Département rattaché
3. Sauvegarder et relancer l'application

#### Méthode 2 : Modifier le code d'initialisation
Dans `app.py`, section `initialiser_fichiers()`, modifier :
```python
equipements_init = pd.DataFrame({
    "id_equipement": ["EQ001", "EQ002", ...],
    "nom_equipement": ["Nom 1", "Nom 2", ...],
    "departement": ["Dept 1", "Dept 2", ...]
})
```

### Modifier les chemins de fichiers

Dans `app.py`, section CONFIGURATION :
```python
DATA_DIR = "data"  # Modifier si nécessaire
EQUIPEMENTS_FILE = os.path.join(DATA_DIR, "equipements.xlsx")
OBSERVATIONS_FILE = os.path.join(DATA_DIR, "observations.csv")
```

---

## 🏗️ Architecture technique

### Stack technologique
- **Frontend** : Streamlit (interface web Python)
- **Traitement de données** : Pandas
- **Stockage** : Fichiers CSV/Excel
- **Export** : openpyxl

### Modèle de données

#### Table : Équipements
```sql
id_equipement   VARCHAR(10)  PRIMARY KEY
departement     VARCHAR(50)  NOT NULL
```

#### Table : Observations
```sql
id_equipement   VARCHAR(10)  FOREIGN KEY -> equipements.id_equipement
date            DATE         NOT NULL
observation     TEXT         NOT NULL
recommandation  TEXT
Trav_notes      TEXT
analyste        VARCHAR(50)  NOT NULL
```

### Fonctions principales

#### `initialiser_fichiers()`
Crée les fichiers de données avec structure initiale si absents.

#### `charger_equipements() -> DataFrame`
Charge et valide les équipements depuis Excel.

#### `charger_observations() -> DataFrame`
Charge et valide les observations depuis CSV.

#### `sauvegarder_observation(...) -> bool`
Enregistre une nouvelle observation dans le CSV.

#### `exporter_excel(...) -> BytesIO`
Génère un fichier Excel avec fusion des données.

### Gestion des erreurs
- Validation des colonnes requises
- Messages d'erreur explicites dans l'interface
- Try/except sur toutes les opérations I/O
- Valeurs par défaut pour DataFrames vides

---

## 🔮 Évolutions futures

### Phase 2 : Améliorations immédiates
- [ ] Authentification basique (streamlit-authenticator)
- [ ] Pièces jointes (photos, PDF)
- [ ] Recherche textuelle dans observations
- [ ] Statistiques par département

### Phase 3 : Base de données
- [ ] Migration vers SQLite
- [ ] Gestion transactionnelle
- [ ] Performances optimisées (>1000 observations)
- [ ] Historique des modifications

### Phase 4 : Fonctionnalités avancées
- [ ] Notifications par email
- [ ] Planification des maintenances
- [ ] Tableau de bord avec graphiques (Plotly)
- [ ] Export PDF avec mise en page
- [ ] API REST pour intégration GMAO

### Phase 5 : Enterprise
- [ ] PostgreSQL multi-utilisateurs
- [ ] Rôles et permissions (admin/analyste/lecteur)
- [ ] Audit trail complet
- [ ] Intégration LDAP/Active Directory
- [ ] Déploiement Docker

---

## 🤝 Contribution

### Standards de code
- **Formatage** : Respecter PEP 8
- **Docstrings** : Format Google Style
- **Type hints** : Encouragés pour les fonctions principales
- **Commentaires** : En français pour ce projet

### Workflow Git
```bash
# Créer une branche pour une nouvelle fonctionnalité
git checkout -b feature/ma-fonctionnalite

# Commiter avec des messages explicites
git commit -m "feat: ajout recherche textuelle"

# Pousser et créer une pull request
git push origin feature/ma-fonctionnalite
```

### Conventions de commit
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation uniquement
- `refactor:` refactorisation sans changement fonctionnel
- `test:` ajout de tests

---

## 🐛 Support et dépannage

### Problèmes courants

#### L'application ne démarre pas
```bash
# Vérifier la version de Python
python --version  # Doit être >= 3.8

# Réinstaller les dépendances
pip install --upgrade streamlit pandas openpyxl
```

#### Erreur "Colonnes manquantes"
- Vérifier que `equipements.xlsx` contient : `id_equipement`, `departement`
- Vérifier que `observations.csv` contient : `id_equipement`, `date`, `observation`, `recommandation`, 'Travaux effectués et Notes", `analyste`

#### Les données ne se sauvegardent pas
- Vérifier les permissions d'écriture dans le dossier `data/`
- Consulter les logs dans le terminal Streamlit

#### Export Excel ne fonctionne pas
```bash
# Réinstaller openpyxl
pip install --force-reinstall openpyxl
```

### Logs et débogage

Les messages d'erreur s'affichent :
1. Dans l'interface Streamlit (messages rouges)
2. Dans le terminal (logs détaillés)

Pour activer le mode debug :
```bash
streamlit run app.py --logger.level=debug
```

---

## 📞 Contact

Pour toute question ou suggestion :
- **Email** : zaravitamds18@gmail.com
- **Partenaire** : ANDRIAMASINADY Angelico
- **Documentation** : …
---

## 📄 Licence

Usage interne uniquement - Propriété de Partenariat de M. Angelico et M. ZARAVITA
© 2025 - Tous droits réservés

---

## 📚 Ressources

### Documentation officielle
- [Streamlit](https://docs.streamlit.io/)
- [Pandas](https://pandas.pydata.org/docs/)
- [openpyxl](https://openpyxl.readthedocs.io/)

### Tutoriels recommandés
- [Streamlit for Data Apps](https://streamlit.io/gallery)
- [Pandas Cheat Sheet](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf)

---

**Version** : 1.0.0 (MVP)  
**Dernière mise à jour** : Janvier 2025  
**Statut** : ✅ Production-ready pour usage interne