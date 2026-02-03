# 🔧 Application de Gestion des Rapports de Maintenance

Application professionnelle Streamlit pour le suivi des équipements industriels, leurs observations de maintenance et l'analyse de tendances vibratoires.

## 📋 Description

Cette application permet de :
- **Gérer un référentiel d'équipements** organisés par département
- **Enregistrer et consulter des observations** de maintenance
- **Analyser les tendances** de mesures vibratoires (vitesse, TWF RMS, Crest Factor, etc.)
- **Visualiser graphiquement** l'évolution des métriques dans le temps
- **Exporter des rapports Excel** professionnels avec graphiques intégrés
- **Supprimer des données** avec système de double confirmation

## 🎯 Fonctionnalités principales

### 📦 Onglet Équipements
- Ajout d'équipements avec départements (existants ou nouveaux)
- Visualisation et filtrage par département
- Statistiques par département
- Export Excel avec mise en forme professionnelle

### 📝 Onglet Observations
- Saisie rapide d'observations de maintenance
- Formulaire structuré : observation, recommandation, travaux effectués & notes, analyse et importance
- saisie de suivi des mesures
- Historique filtrable (département, équipement, période)
- **Visualisation graphique des tendances** :
  - Sélection d'équipement et point de mesure
  - 4 variables disponibles : Vitesse (RPM), TWF RMS (g), Crest Factor, TWF Peak-to-Peak (g)
  - Filtrage par période personnalisée ou 22 dernières observations
  - Statistiques détaillées (min, max, moyenne, écart-type)

### 📥 Onglet Téléchargements
- **Rapport d'observations** : Export Excel avec filtres avancés
- **Liste des équipements** : Export du référentiel complet
- **Rapport de suivi de mesures** : 
  - Un onglet par équipement
  - Tableaux de données avec formatage professionnel
  - Graphiques interactifs avec menus déroulants (point de mesure + métrique)
  - Format dates DD/MM/YYYY

### 🗑️ Onglet Suppressions
- Suppression ciblée d'observations (par département, équipement, date)
- Suppression de suivis de mesure (par département, équipement, point de mesure, date)
- Suppression d'équipements (avec toutes observations et suivis associés)
- Système de double confirmation pour éviter les erreurs

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Étapes d'installation

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

### Dépendances principales
```
streamlit
pandas
openpyxl
plotly
requests
```

4. **Créer la structure des dossiers**
```bash
mkdir data
mkdir ui
```

5. **Copier les fichiers Python** dans leur emplacement respectif

## 📂 Structure du projet

```
maintenance-app/
│
├── app.py                              # Point d'entrée principal
├── requirements.txt                    # Dépendances Python
│
├── data/                               # Répertoire données (créé automatiquement)
│   ├── equipements.xlsx                # Référentiel équipements
│   ├── observations.csv                # Historique observations
│   ├── suivi_equipements_enrichi.csv   # Données de suivi vibratoire
│   └── data_manager.py                 # Couche d'accès données (CRUD)
│
└── ui/                                 # Modules d'interface
    ├── equipements.py                  # Onglet Équipements
    ├── observations.py                 # Onglet Observations + Graphiques
    ├── telechargements.py              # Onglet Téléchargements
    └── suppressions.py                 # Onglet Suppressions
```

## 🎮 Utilisation

### Lancement de l'application

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse `http://localhost:8501`

## 📖 Guide d'utilisation détaillé

### 1️⃣ Onglet Équipements

**Objectif** : Gérer le référentiel des équipements

**Fonctionnalités** :

**Bloc 1 - Ajout d'équipement** :
- Mode "Département existant" ou "Nouveau département"
- Saisie de l'ID équipement
- Validation en temps réel
- Détection des doublons

**Bloc 2 - Liste et filtres** :
- Tableau de tous les équipements
- Filtrage multi-sélection par département(s)
- Compteur dynamique de résultats
- Tri automatique par département et ID

**Bloc 3 - Export Excel** :
- Export des équipements filtrés ou complets
- Nom de fichier intelligent (avec département si filtre unique)
- Format professionnel avec en-têtes formatés

**Bloc 4 - Statistiques** :
- Nombre d'équipements par département
- Tri décroissant
- Total général

**Cas d'usage** :
- Ajouter rapidement un nouvel équipement
- Consulter la liste des équipements d'un département
- Exporter le référentiel pour un rapport
- Vérifier le nombre d'équipements par zone

### 2️⃣ Onglet Observations

**Objectif** : Saisir, consulter l'historique et analyser les tendances

**Bloc 1 - Nouvelle observation** :
1. Sélectionner le département (hors formulaire pour réactivité)
2. Choisir l'équipement (liste filtrée automatiquement)
3. Définir la date (par défaut : aujourd'hui)
4. Remplir les champs :
   - **Observation*** : Description de l'état constaté (requis)
   - **Recommandation** : Actions à entreprendre (optionnel)
   - **Travaux effectués & Notes** : Travaux réalisés (optionnel)
   - **Analyste*** : Nom de l'analyste (requis)
5. Cliquer sur "✅ Enregistrer"
6. Le formulaire se vide automatiquement pour une nouvelle saisie

**Bloc 2 - Historique des observations** :
- **Affichage par défaut** : 5 observations les plus récentes
- **Filtres disponibles** :
  - Département(s) - Multi-sélection
  - Équipement(s) - Cascade avec département
  - Période - Date début/fin avec calendrier
- **Tableau complet** : Tous les champs avec colonnes ajustées
- **Tri** : Par date décroissante (plus récent en haut)
- **Compteur** : Nombre d'observations affichées

**Bloc 3 - Visualisation des tendances** :
- **Sélection de l'équipement** : ID équipement
- **Sélection du point de mesure** : Liste dynamique selon équipement
- **Modes de filtrage temporel** :
  - "Période personnalisée" : Choisir date début/fin
  - "22 dernières observations" : Fenêtre glissante
- **Variables disponibles** (multi-sélection) :
  - Vitesse (RPM)
  - TWF RMS (g)
  - Crest Factor
  - TWF Peak-to-Peak (g)
- **Graphique interactif** :
  - Lignes avec marqueurs
  - Zoom et pan
  - Hover pour détails
  - Légende activable/désactivable
  - Export image intégré
- **Statistiques détaillées** (expander) :
  - Min, Max, Moyenne, Écart-type pour chaque variable

**Cas d'usage** :
- Saisir rapidement une observation après une ronde
- Consulter l'historique d'un équipement problématique
- Identifier des tendances de dégradation via graphiques
- Vérifier les recommandations passées
- Analyser l'évolution vibratoire sur une période

### 3️⃣ Onglet Téléchargements

**Objectif** : Générer des exports Excel professionnels et filtrés

**Carte 1 - Rapport d'observations** :
- **Filtres disponibles** :
  - Département(s) - Multi-sélection
  - Équipement(s) - Filtré par département
  - Date début - Calendrier
  - Date fin - Calendrier
- **Informations affichées** :
  - Nombre d'observations à exporter
  - Départements sélectionnés
  - Équipements sélectionnés
  - Période d'export
- **Format du fichier** :
  - Colonnes : Département, ID Équipement, Date, Observation, Recommandation, Travaux & Notes, Analyste, Importance
  - En-têtes formatés (fond bleu, texte blanc, gras)
  - Bordures sur toutes les cellules
  - Colonnes auto-ajustées
  - Dates au format DD/MM/YYYY
  - Tri par date décroissante
  - Ligne d'en-tête figée
- **Nom du fichier** : `rapport_observations_YYYYMMDD_HHMM.xlsx`

**Carte 2 - Liste des équipements** :
- **Filtre** : Département(s)
- **Format** : Tableau simple avec ID et Département
- **Tri** : Par département puis ID
- **Nom du fichier** : `equipements_YYYYMMDD_HHMM.xlsx`

**Carte 3 - Rapport de suivi de mesures** :
- **Filtres disponibles** :
  - ID Équipement(s) - Multi-sélection
  - Point(s) de mesure - Filtré par équipement
  - Date début - Calendrier
  - Date fin - Calendrier
- **Informations affichées** :
  - Nombre d'équipements
  - Nombre de mesures totales
  - Équipements sélectionnés
  - Points de mesure
  - Période d'export
- **Structure du fichier Excel** :
  - **Un onglet par équipement**
  - **Tableaux de données** organisés par point de mesure
  - **Graphiques Excel interactifs** avec :
    - Menu déroulant 1 : Sélection du point de mesure
    - Menu déroulant 2 : Sélection de la métrique (Vitesse, TWF RMS, Crest Factor, TWF Peak-to-Peak)
    - Graphique dynamique qui s'adapte aux sélections
    - Formules Excel natives pour compatibilité totale
- **Format professionnel** :
  - En-têtes formatés avec fond coloré
  - Bordures sur les cellules
  - Dates formatées DD/MM/YYYY
  - Colonnes ajustées
- **Nom du fichier** : `rapport_suivi_mesures_YYYYMMDD_HHMM.xlsx`

**Informations complémentaires** (expander) :
- Détails sur les formats d'export
- Encodage UTF-8
- Colonnes auto-ajustées

**Cas d'usage** :
- Générer un rapport mensuel pour la direction
- Exporter les observations d'un équipement pour analyse
- Partager les données avec un sous-traitant
- Archiver les données périodiquement
- Créer des présentations avec graphiques Excel professionnels

### 4️⃣ Onglet Suppressions

**⚠️ Zone critique - Utilisation contrôlée**

**Objectif** : Corriger des erreurs de saisie avec sécurité maximale

**Carte 1 - Supprimer une observation** :
1. Sélectionner le département (réactivité)
2. Choisir l'équipement (liste filtrée avec observations uniquement)
3. Sélectionner la date de l'observation
4. Cliquer sur "🗑️ Supprimer"
5. **Confirmation obligatoire** :
   - Affichage récapitulatif (département, équipement, date)
   - Boutons "✅ Confirmer" ou "❌ Annuler"
6. Message de succès et rechargement automatique

**Carte 2 - Supprimer un suivi de mesure** :
1. Sélectionner le département
2. Choisir l'équipement (liste filtrée avec suivis uniquement)
3. Sélectionner le point de mesure
4. Sélectionner la date du suivi
5. Cliquer sur "🗑️ Supprimer"
6. **Confirmation obligatoire** :
   - Affichage récapitulatif complet avec valeurs des mesures
   - Boutons "✅ Confirmer" ou "❌ Annuler"
7. Suppression uniquement de l'enregistrement ciblé

**Carte 3 - Supprimer un équipement** :
1. Sélectionner le département
2. Choisir l'équipement à supprimer
3. Affichage du nombre d'observations et suivis associés
4. Cliquer sur "🗑️ Supprimer"
5. **⚠️ ATTENTION** - Avertissement critique :
   - Suppression de l'équipement du référentiel
   - Suppression de TOUTES les observations associées
   - Suppression de TOUS les suivis associés
   - **Action irréversible**
6. **Double confirmation obligatoire** :
   - Message d'alerte en rouge
   - Boutons "✅ Confirmer suppression" ou "❌ Annuler"

**Informations de sécurité** (expander) :
- Règles importantes détaillées
- Impact de chaque type de suppression
- Bonnes pratiques recommandées
- Rappel : aucune récupération possible

**Bonnes pratiques** :
- **Exportez vos données avant toute suppression importante**
- Vérifiez toujours les informations affichées dans la confirmation
- Les suppressions sont irréversibles
- En cas de doute, consultez un responsable
- Utilisez cette fonctionnalité uniquement pour corriger des erreurs

**Cas d'usage** :
- Corriger une observation saisie par erreur
- Supprimer une mesure erronée (capteur défaillant)
- Retirer un équipement déclassé avec tout son historique

## 📊 Format des données


| Colonne | Type | Description |
|---------|------|-------------|
| id_equipement | string | Identifiant unique (ex: "244-3P-1") |
| departement | string | Nom du département |

### Observations (observations.csv)
| Colonne | Type | Description |
|---------|------|-------------|
| id_equipement | string | Référence équipement |
| date | date | Date de l'observation |
| observation | string | Description de l'état constaté |
| recommandation | string | Actions recommandées |
| Travaux effectués & Notes | string | Travaux réalisés |
| analyste | string | Nom de l'analyste |

### Suivi vibratoire (suivi_equipements_enrichi.csv)
| Colonne | Type | Description |
|---------|------|-------------|
| id_equipement | string | Référence équipement |
| point_mesure | string | Point de mesure |
| date | date | Date de mesure |
| vitesse_rpm | float | Vitesse en tours/minute |
| twf_rms_g | float | TWF RMS en g |
| crest_factor | float | Facteur de crête |
| twf_peak_to_peak_g | float | TWF crête-à-crête en g |

## 🔐 Sécurité des données

- **Pas de suppression accidentelle** : système de double confirmation
- **Sauvegarde automatique** : toutes les modifications sont persistées immédiatement
- **Export régulier recommandé** : utilisez l'onglet Téléchargements pour des backups

## 🎨 Fonctionnalités avancées

### Graphiques interactifs (Observations)
- **Multi-variables** : jusqu'à 4 métriques simultanées
- **Zoom et pan** : navigation interactive dans les graphiques
- **Hover details** : valeurs détaillées au survol
- **Légende dynamique** : activation/désactivation des séries

### Exports Excel professionnels
- **Formatage automatique** : en-têtes colorés, bordures, alignement
- **Colonnes auto-ajustées** : largeur optimale pour la lisibilité
- **Dates formatées** : format DD/MM/YYYY standard
- **Graphiques Excel** : courbes de tendances avec menus déroulants interactifs

### Filtres intelligents
- **Filtres en cascade** : département → équipement → date
- **Compteurs dynamiques** : nombre de résultats affichés en temps réel
- **Sélection multiple** : plusieurs départements/équipements simultanément

## 🛠️ Architecture technique

### Séparation des responsabilités

**`app.py`** : Point d'entrée principal avec navigation par onglets  
**`data/data_manager.py`** : Couche d'accès aux données - toutes les opérations CRUD  
**`ui/equipements.py`** : Interface de gestion du référentiel équipements  
**`ui/observations.py`** : Interface de saisie, historique et graphiques de tendances  
**`ui/telechargements.py`** : Interface d'export Excel avec formatage professionnel  
**`ui/suppressions.py`** : Interface de suppression sécurisée avec double confirmation  

### Choix techniques

- **Stockage** : Excel (équipements) + CSV (observations, suivi) - Migration Supabase prévue
- **Framework UI** : Streamlit pour développement rapide et UX réactive
- **Manipulation données** : Pandas pour le traitement des DataFrames
- **Visualisation** : Plotly pour graphiques interactifs
- **Export Excel** : openpyxl pour formatage avancé et graphiques natifs

### Architecture modulaire

```python
# Exemple de flux de données
app.py (Navigation)
    ↓
ui/observations.py (Interface)
    ↓
data/data_manager.py (Logique métier)
    ↓
Fichiers CSV/Excel (Stockage)
```

### Points de migration Supabase

Les fonctions dans `data_manager.py` sont conçues pour être facilement migrées vers Supabase :

```python
# Actuellement : Stockage fichiers
def charger_observations():
    return pd.read_csv(OBSERVATIONS_FILE, parse_dates=["date"])

# Future migration Supabase :
def charger_observations():
    response = supabase.table('observations').select('*').execute()
    return pd.DataFrame(response.data)
```

**Fonctions à migrer** :
- `charger_equipements()` → `supabase.table('equipements').select('*')`
- `charger_observations()` → `supabase.table('observations').select('*')`
- `charger_suivi()` → `supabase.table('suivi').select('*')`
- `sauvegarder_observation()` → `supabase.table('observations').insert()`
- `supprimer_observation()` → `supabase.table('observations').delete()`
- `supprimer_equipement()` → Transaction avec cascade sur observations
- `supprimer_suivi()` → `supabase.table('suivi').delete()`

**Avantages de la migration** :
- Accès multi-utilisateurs simultané
- Transactions ACID
- Authentification intégrée
- API temps réel
- Backup automatique
- Scalabilité

## 🎨 Conventions de code

### Style
- **Noms de fonctions** : `snake_case`
- **Commentaires** : Français (contexte métier industriel)
- **Docstrings** : Format Google avec types et returns
- **Variables** : Noms explicites (pas d'abréviations cryptiques)

### Organisation
- **Un onglet = un fichier** dans `ui/`
- **Logique métier** uniquement dans `data_manager.py`
- **UI pure** dans les modules `ui/` (pas de manipulation de fichiers)
- **Séparation claire** : Interface ≠ Logique ≠ Données

## 🔧 Maintenance et administration

### Ajouter un équipement manuellement

Si besoin d'éditer directement le fichier `data/equipements.xlsx` :

| id_equipement | departement |
|---------------|-------------|
| NOUVEAU-ID-123 | NOM_DEPARTEMENT |

**⚠️ Attention** : Respectez exactement les noms de colonnes et le format.

### Sauvegarder les données

**Méthode recommandée** : Utiliser l'onglet "📥 Téléchargements"

**Méthode manuelle** : Copier les fichiers régulièrement
```bash
# Créer un dossier de sauvegarde
mkdir backups

# Copier les fichiers avec horodatage
cp data/equipements.xlsx backups/equipements_$(date +%Y%m%d).xlsx
cp data/observations.csv backups/observations_$(date +%Y%m%d).csv
cp data/suivi_equipements_enrichi.csv backups/suivi_$(date +%Y%m%d).csv
```

**Fréquence recommandée** :
- Sauvegarde quotidienne automatique (via cron ou tâche planifiée)
- Export manuel hebdomadaire via l'application
- Sauvegarde avant toute opération de suppression importante

### Réinitialiser les données

Pour repartir avec des données exemples :

```bash
# Supprimer le dossier data
rm -rf data/

# Relancer l'application - les fichiers seront recréés
streamlit run app.py
```

**⚠️ Attention** : Cette opération supprime toutes vos données. Faites une sauvegarde avant !

### Vérifier l'intégrité des données

```python
# Script de vérification (à exécuter dans Python)
import pandas as pd

# Vérifier équipements
df_equip = pd.read_excel('data/equipements.xlsx')
print(f"✅ {len(df_equip)} équipements chargés")
print(f"Départements : {df_equip['departement'].nunique()}")

# Vérifier observations
df_obs = pd.read_csv('data/observations.csv')
print(f"✅ {len(df_obs)} observations chargées")

# Vérifier suivi
df_suivi = pd.read_csv('data/suivi_equipements_enrichi.csv')
print(f"✅ {len(df_suivi)} mesures de suivi chargées")
```

## 📈 Cas d'usage

### Maintenance préventive
Suivez l'évolution des mesures vibratoires pour détecter les anomalies avant défaillance.

### Rapports périodiques
Exportez des rapports mensuels/trimestriels pour la direction ou les équipes terrain.

### Analyse de défaillances
Consultez l'historique complet d'un équipement pour comprendre les causes d'une panne.

### Gestion de parc
Visualisez la répartition de vos équipements par département et leur état.

## 🐛 Dépannage

### L'application ne démarre pas

**Symptômes** : Erreur au lancement de `streamlit run app.py`

**Solutions** :
```bash
# 1. Vérifier les dépendances
pip install -r requirements.txt --upgrade

# 2. Vérifier la version Python (doit être ≥ 3.8)
python --version

# 3. Vérifier que le fichier app.py est présent
ls app.py

# 4. Essayer avec un environnement virtuel propre
python -m venv venv_test
source venv_test/bin/activate  # ou venv_test\Scripts\activate sur Windows
pip install -r requirements.txt
streamlit run app.py
```

### Erreur "Colonnes manquantes"

**Symptômes** : Message d'erreur au chargement des données

**Causes possibles** :
- Fichiers Excel/CSV corrompus
- Structure des colonnes modifiée manuellement
- Encodage incorrect

**Solutions** :
```bash
# 1. Vérifier la structure des fichiers
python -c "import pandas as pd; print(pd.read_excel('data/equipements.xlsx').columns.tolist())"

# 2. Si corrompu, restaurer depuis backup
cp backups/equipements_YYYYMMDD.xlsx data/equipements.xlsx

# 3. Dernière option : réinitialiser (⚠️ perte de données)
rm -rf data/
streamlit run app.py
```

### Graphiques ne s'affichent pas

**Symptômes** : Zone vide dans "Visualisation des tendances"

**Solutions** :
1. **Rafraîchir la page** (F5 ou Ctrl+R)
2. **Vérifier les données** : Assurez-vous que l'équipement sélectionné a des données de suivi
3. **Vérifier la console** : Ouvrir la console Streamlit pour voir les erreurs
4. **Vider le cache Streamlit** :
   ```bash
   streamlit cache clear
   ```

### Données non sauvegardées

**Symptômes** : Les observations disparaissent après fermeture

**Causes possibles** :
- Permissions d'écriture insuffisantes
- Disque plein
- Antivirus bloquant l'écriture

**Solutions** :
```bash
# 1. Vérifier les permissions du dossier data/
ls -la data/

# 2. Changer les permissions si nécessaire (Linux/Mac)
chmod 755 data/
chmod 644 data/*.csv data/*.xlsx

# 3. Vérifier l'espace disque
df -h

# 4. Tester l'écriture manuellement
touch data/test.txt && rm data/test.txt && echo "✅ Écriture OK"
```

### Export Excel corrompu

**Symptômes** : Le fichier Excel téléchargé ne s'ouvre pas

**Solutions** :
1. Réessayer l'export
2. Vérifier que openpyxl est à jour : `pip install --upgrade openpyxl`
3. Utiliser un autre navigateur
4. Vérifier l'antivirus (peut bloquer le téléchargement)

### Performance lente

**Symptômes** : L'application met du temps à répondre

**Causes** :
- Trop de données chargées en mémoire
- Filtres non appliqués

**Solutions** :
1. **Utiliser les filtres** pour limiter les données affichées
2. **Archiver les anciennes données** :
   ```bash
   # Exporter puis supprimer observations > 2 ans
   ```
3. **Augmenter la mémoire Streamlit** :
   ```bash
   streamlit run app.py --server.maxUploadSize 1000
   ```

### Erreur d'encodage (caractères spéciaux)

**Symptômes** : Accents ou caractères spéciaux mal affichés

**Solutions** :
```python
# Forcer l'encodage UTF-8 lors de la lecture CSV
df = pd.read_csv('data/observations.csv', encoding='utf-8')

# Si problème persiste, essayer avec latin1
df = pd.read_csv('data/observations.csv', encoding='latin1')
```

## 🔄 Évolutions futures

### Version 3.0 (Prévue)
- [ ] **Migration vers Supabase** (base de données cloud)
- [ ] **Authentification utilisateurs** avec rôles (admin, analyste, lecteur)
- [ ] **Historique des modifications** (audit trail)
- [ ] **Notifications automatiques** (seuils dépassés, maintenance due)
- [ ] **Dashboard de synthèse** avec KPIs et alertes

### Version 3.5 (Explorée)
- [ ] **Pièces jointes** : Upload de photos, PDFs, rapports
- [ ] **Tableau de bord analytique** : Prédictions de défaillances
- [ ] **API REST** pour intégration externe (CMMS, ERP)
- [ ] **Application mobile** React Native ou Flutter
- [ ] **Export PDF** avec mise en page personnalisée
- [ ] **Planification maintenance** avec calendrier intégré

### Fonctionnalités en cours d'évaluation
- **Intelligence Artificielle** : Détection d'anomalies automatique
- **Rapports automatiques** : Génération hebdomadaire/mensuelle par email
- **Intégration capteurs IoT** : Import automatique des mesures
- **Chatbot support** : Assistance guidée pour les utilisateurs

## 👥 Contribution et Support

### Pour les développeurs

Ce projet suit une architecture modulaire pour faciliter les contributions :

1. **Fork** le projet
2. Créer une **branche feature** : `git checkout -b feature/nouvelle-fonctionnalite`
3. **Commiter** les changements : `git commit -m 'Ajout nouvelle fonctionnalité'`
4. **Push** vers la branche : `git push origin feature/nouvelle-fonctionnalite`
5. Ouvrir une **Pull Request**

### Standards de code
- Tests unitaires requis pour nouvelle logique métier
- Documentation des fonctions (docstrings)
- Respect des conventions PEP 8
- Messages de commit en français

### Support utilisateurs

Pour toute question, problème ou suggestion :

📧 **Email** : maintenance@entreprise.com  
📱 **Téléphone** : +212 770 636 297 
💬 **Slack** : #maintenance-support  
📝 **Documentation** : Wiki interne  

**Délai de réponse** :
- Questions urgentes : < 4h ouvrées
- Bugs bloquants : < 24h
- Demandes d'évolution : < 1 semaine

## 📝 Licence et propriété intellectuelle

**Projet interne** - Tous droits réservés  
**Confidentialité** : Ne pas diffuser en dehors de l'entreprise  
**Usage** : Réservé aux équipes maintenance et production  

---

## 📌 Informations de version

**Version actuelle** : 2.5.0  
**Date de version** : Février 2026  
**Statut** : ✅ Production stable  

**Changelog** :
- **v2.5.0** (Février 2026)
  - ✨ Ajout visualisation graphique des tendances (Plotly)
  - ✨ Export Excel avec graphiques interactifs (menus déroulants)
  - ✨ Suppression de suivis de mesure
  - 🎨 Interface améliorée avec blocs structurés
  - 📊 Statistiques détaillées dans les graphiques
  - 🐛 Corrections mineures et optimisations

- **v2.0.0** (Janvier 2025)
  - 🔨 Refactorisation complète avec architecture modulaire
  - ✨ Système de suppressions sécurisé
  - ✨ Exports Excel professionnels
  - 🎨 Interface par onglets
  - 📁 Séparation ui/ et data/

- **v1.0.0** (Décembre 2024)
  - 🎉 Version initiale
  - ✅ Gestion équipements et observations
  - 📥 Exports basiques

---

**Développé avec ❤️ par ZARAVITA & A. Angelico pour l'équipe Maintenance**