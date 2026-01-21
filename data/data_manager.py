"""
Module de gestion des données (Excel/CSV)
Prêt pour migration future vers Supabase
"""

import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_DIR = "data"
EQUIPEMENTS_FILE = os.path.join(DATA_DIR, "equipements.xlsx")
OBSERVATIONS_FILE = os.path.join(DATA_DIR, "observations.csv")

# Schéma des données
EQUIPEMENTS_COLS = ["id_equipement", "departement"]
OBSERVATIONS_COLS = [
    "id_equipement", "date", "observation",
    "recommandation", "Travaux effectués & Notes", "analyste"
]


# =============================================================================
# INITIALISATION
# =============================================================================


def initialiser_fichiers():
    """Crée les fichiers de données s'ils n'existent pas"""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Initialiser équipements avec données exemples
    if not os.path.exists(EQUIPEMENTS_FILE):
        equipements_init = pd.DataFrame({
            "id_equipement": ["244-3P-1", "262-1P-4", "32-1H-3", "25-24P", "44-43P"],
            "departement": ["Chargement", "CHAUFFERIE", "CHLORE 1", "ELECTROLYSE 1", "ÉVAPO 1"]
        })
        equipements_init.to_excel(EQUIPEMENTS_FILE, index=False)

    # Initialiser observations vide
    if not os.path.exists(OBSERVATIONS_FILE):
        observations_init = pd.DataFrame(columns=OBSERVATIONS_COLS)
        observations_init.to_csv(OBSERVATIONS_FILE, index=False)


# =============================================================================
# LECTURE DES DONNÉES
# =============================================================================

def charger_equipements():
    """
    Charge la liste des équipements depuis Excel

    Returns:
        DataFrame: Équipements avec colonnes [id_equipement, departement]
    """
    try:
        df = pd.read_excel(EQUIPEMENTS_FILE)
        if not all(col in df.columns for col in EQUIPEMENTS_COLS):
            raise ValueError(f"Colonnes manquantes dans {EQUIPEMENTS_FILE}")
        return df
    except Exception as e:
        print(f"Erreur chargement équipements: {e}")
        return pd.DataFrame(columns=EQUIPEMENTS_COLS)


def charger_observations():
    """
    Charge l'historique des observations depuis CSV

    Returns:
        DataFrame: Observations avec dates parsées
    """
    try:
        df = pd.read_csv(OBSERVATIONS_FILE,
                         parse_dates=["date"],
                         encoding='utf-8')
        if not all(col in df.columns for col in OBSERVATIONS_COLS):
            raise ValueError(f"Colonnes manquantes dans {OBSERVATIONS_FILE}")
        return df
    except Exception as e:
        print(f"Erreur chargement observations: {e}")
        return pd.DataFrame(columns=OBSERVATIONS_COLS)


# =============================================================================
# ÉCRITURE DES DONNÉES
# =============================================================================

def sauvegarder_observation(id_equipement, date, observation, recommandation, trav_notes, analyste):
    """
    Enregistre une nouvelle observation

    Args:
        id_equipement (str): Identifiant équipement
        date (datetime): Date observation
        observation (str): Texte observation
        recommandation (str): Texte recommandation
        trav_notes (str): Travaux effectués & notes
        analyste (str): Nom analyste

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        df_obs = charger_observations()

        nouvelle_obs = pd.DataFrame([{
            "id_equipement": id_equipement,
            "date": pd.to_datetime(date),    #date.strftime("%Y-%m-%d") #-----------------------------------------------
            "observation": observation,
            "recommandation": recommandation,
            "Travaux effectués & Notes": trav_notes,
            "analyste": analyste
        }])
        # ✅ S'assurer que la colonne date est bien en datetime avant sauvegarde ---------------------------------------
        df_obs['date'] = pd.to_datetime(df_obs['date'])  #------------------------------------------------------------

        df_obs = pd.concat([df_obs, nouvelle_obs], ignore_index=True)
        df_obs.to_csv(OBSERVATIONS_FILE,
                      index=False,
                      encoding='utf-8')

        return True, "✅ Observation enregistrée avec succès"
    except Exception as e:
        return False, f"❌ Erreur lors de la sauvegarde : {e}"


# =============================================================================
# SUPPRESSIONS
# =============================================================================

def supprimer_observation(id_equipement, date):
    """
    Supprime une observation spécifique

    Args:
        id_equipement (str): ID équipement
        date (datetime.date): Date observation

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        df_obs = charger_observations()

        # Convertir date pour comparaison
        df_obs['date'] = pd.to_datetime(df_obs['date']).dt.date
        date_cible = pd.to_datetime(date).date()

        # Vérifier existence
        mask = (df_obs['id_equipement'] == id_equipement) & (df_obs['date'] == date_cible)
        if not mask.any():
            return False, "⚠️ Aucune observation trouvée pour cet équipement et cette date"

        # Supprimer
        df_obs = df_obs[~mask]

        # Reconvertir en datetime avant sauvegarde
        df_obs['date'] = pd.to_datetime(df_obs['date'])
        df_obs.to_csv(OBSERVATIONS_FILE, index=False)

        return True, "✅ Observation supprimée avec succès"
    except Exception as e:
        return False, f"❌ Erreur lors de la suppression : {e}"


def supprimer_equipement(id_equipement):
    """
    Supprime un équipement ET toutes ses observations associées

    Args:
        id_equipement (str): ID équipement à supprimer

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Charger équipements
        df_equip = charger_equipements()

        # Vérifier existence
        if id_equipement not in df_equip['id_equipement'].values:
            return False, "⚠️ Équipement non trouvé"

        # Supprimer équipement
        df_equip = df_equip[df_equip['id_equipement'] != id_equipement]
        df_equip.to_excel(EQUIPEMENTS_FILE, index=False)

        # Supprimer observations associées
        df_obs = charger_observations()
        nb_obs_supprimees = len(df_obs[df_obs['id_equipement'] == id_equipement])
        df_obs = df_obs[df_obs['id_equipement'] != id_equipement]
        df_obs.to_csv(OBSERVATIONS_FILE, index=False)

        msg = f"✅ Équipement supprimé ({nb_obs_supprimees} observation(s) associée(s) supprimée(s))"
        return True, msg
    except Exception as e:
        return False, f"❌ Erreur lors de la suppression : {e}"


# =============================================================================
# EXPORTS
# =============================================================================

def exporter_observations_excel(df_observations, df_equipements):
    """
    Génère un fichier Excel avec observations enrichies

    Args:
        df_observations (DataFrame): Observations filtrées
        df_equipements (DataFrame): Référentiel équipements

    Returns:
        BytesIO: Buffer contenant fichier Excel
    """
    # Fusion
    df_export = df_observations.merge(
        df_equipements[['id_equipement', 'departement']],
        on='id_equipement',
        how='left'
    )

    # Colonnes export
    colonnes = [
        'departement', 'id_equipement', 'date',
        'observation', 'recommandation',
        'Travaux effectués & Notes', 'analyste'
    ]

    df_export = df_export[colonnes].copy()

    # Renommage pour clarté
    df_export.columns = [
        'Département', 'ID Équipement', 'Date',
        'Observation', 'Recommandation',
        'Travaux effectués & Notes', 'Analyste'
    ]

    # Tri par date décroissante
    df_export = df_export.sort_values('Date', ascending=False)

    # Conversion Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Observations', index=False)

        # Ajustement colonnes
        worksheet = writer.sheets['Observations']
        for idx, col in enumerate(df_export.columns):
            max_len = max(
                df_export[col].astype(str).map(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_len + 2, 50)

    buffer.seek(0)
    return buffer


def exporter_equipements_excel(df_equipements):
    """
    Génère un fichier Excel avec liste équipements

    Args:
        df_equipements (DataFrame): Équipements filtrés

    Returns:
        BytesIO: Buffer contenant fichier Excel
    """
    df_export = df_equipements.copy()
    df_export.columns = ['ID Équipement', 'Département']
    df_export = df_export.sort_values(['Département', 'ID Équipement'])

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Équipements', index=False)

        worksheet = writer.sheets['Équipements']
        for idx, col in enumerate(df_export.columns):
            max_len = max(
                df_export[col].astype(str).map(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = max_len + 2

    buffer.seek(0)
    return buffer