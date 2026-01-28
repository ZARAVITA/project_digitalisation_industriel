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
SUIVI_FILE = os.path.join(DATA_DIR, "suivi_equipements_enrichi.csv") #--------------------------------------

# Schéma des données
EQUIPEMENTS_COLS = ["id_equipement", "departement"]
OBSERVATIONS_COLS = [
    "id_equipement", "date", "observation",
    "recommandation", "Travaux effectués & Notes", "analyste", "importance"
]
SUIVI_COLS = [
    "id_equipement", "point_mesure", "date",
    "vitesse_rpm", "twf_rms_g", "crest_factor", "twf_peak_to_peak_g"
]

# Points de mesure possibles (liste fermée)
POINTS_MESURE = [
    "M-COA",
    "M-CA",
    "Entrée Réducteur",
    "Sortie Réducteur",
    "P-CA",
    "P-COA"
]

# Options d'importance
OPTIONS_IMPORTANCE = [
    "Important",
    "Pas de collecte mais important",
    "Moins important",
    "Collecte réalisée"
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

    # Initialiser observations vide avec la nouvelle colonne importance
    if not os.path.exists(OBSERVATIONS_FILE):
        observations_init = pd.DataFrame(columns=OBSERVATIONS_COLS)
        observations_init.to_csv(OBSERVATIONS_FILE, index=False, encoding='utf-8')
    else:
        # Migrer les anciennes observations si la colonne importance n'existe pas
        try:
            df_obs = pd.read_csv(OBSERVATIONS_FILE, encoding='utf-8')
            if 'importance' not in df_obs.columns:
                df_obs['importance'] = ""
                df_obs.to_csv(OBSERVATIONS_FILE, index=False, encoding='utf-8')
        except Exception as e:
            print(f"Erreur migration observations: {e}")

    # Initialiser suivi_equipements vide
    if not os.path.exists(SUIVI_FILE):
        suivi_init = pd.DataFrame(columns=SUIVI_COLS)
        suivi_init.to_csv(SUIVI_FILE, index=False, encoding='utf-8')


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


def charger_suivi():
    """
    Charge les données de suivi équipements depuis CSV

    Returns:
        DataFrame: Données de suivi avec dates parsées
    """
    try:
        df = pd.read_csv(SUIVI_FILE,
                         parse_dates=["date"],
                         encoding='utf-8')
        if not all(col in df.columns for col in SUIVI_COLS):
            raise ValueError(f"Colonnes manquantes dans {SUIVI_FILE}")
        return df
    except Exception as e:
        print(f"Erreur chargement suivi: {e}")
        return pd.DataFrame(columns=SUIVI_COLS)


# =============================================================================
# ÉCRITURE DES DONNÉES
# =============================================================================

def sauvegarder_observation(id_equipement, date, observation, recommandation, trav_notes, analyste, importance=""):
    """
    Enregistre une nouvelle observation

    Args:
        id_equipement (str): Identifiant équipement
        date (datetime): Date observation
        observation (str): Texte observation
        recommandation (str): Texte recommandation
        trav_notes (str): Travaux effectués & notes
        analyste (str): Nom analyste
        importance (str): Niveau d'importance

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        df_obs = charger_observations()

        nouvelle_obs = pd.DataFrame([{
            "id_equipement": id_equipement,
            "date": pd.to_datetime(date),
            "observation": observation,
            "recommandation": recommandation,
            "Travaux effectués & Notes": trav_notes,
            "analyste": analyste,
            "importance": importance
        }])

        # S'assurer que la colonne date est bien en datetime avant sauvegarde
        df_obs['date'] = pd.to_datetime(df_obs['date'])

        df_obs = pd.concat([df_obs, nouvelle_obs], ignore_index=True)
        df_obs.to_csv(OBSERVATIONS_FILE,
                      index=False,
                      encoding='utf-8')

        return True, "✅ Observation enregistrée avec succès"
    except Exception as e:
        return False, f"❌ Erreur lors de la sauvegarde : {e}"


def sauvegarder_suivi(id_equipement, point_mesure, date, vitesse_rpm, twf_rms_g, crest_factor, twf_peak_to_peak_g):
    """
    Enregistre une nouvelle mesure de suivi

    Args:
        id_equipement (str): Identifiant équipement
        point_mesure (str): Point de mesure
        date (datetime): Date de collecte
        vitesse_rpm (float): Vitesse en RPM
        twf_rms_g (float): TWF RMS en g
        crest_factor (float): Crest Factor
        twf_peak_to_peak_g (float): TWF Peak to Peak en g

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        df_suivi = charger_suivi()

        nouvelle_mesure = pd.DataFrame([{
            "id_equipement": id_equipement,
            "point_mesure": point_mesure,
            "date": pd.to_datetime(date),
            "vitesse_rpm": round(float(vitesse_rpm), 2),
            "twf_rms_g": round(float(twf_rms_g), 2),
            "crest_factor": round(float(crest_factor), 2),
            "twf_peak_to_peak_g": round(float(twf_peak_to_peak_g), 2)
        }])

        # S'assurer que la colonne date est bien en datetime avant sauvegarde
        df_suivi['date'] = pd.to_datetime(df_suivi['date'])

        df_suivi = pd.concat([df_suivi, nouvelle_mesure], ignore_index=True)
        df_suivi.to_csv(SUIVI_FILE,
                        index=False,
                        encoding='utf-8')

        return True, "✅ Mesure de suivi enregistrée avec succès"
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
        df_obs.to_csv(OBSERVATIONS_FILE, index=False, encoding='utf-8')

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
        df_obs.to_csv(OBSERVATIONS_FILE, index=False, encoding='utf-8')

        # Supprimer données de suivi associées
        df_suivi = charger_suivi()
        nb_suivi_supprimees = len(df_suivi[df_suivi['id_equipement'] == id_equipement])
        df_suivi = df_suivi[df_suivi['id_equipement'] != id_equipement]
        df_suivi.to_csv(SUIVI_FILE, index=False, encoding='utf-8')

        msg = f"✅ Équipement supprimé ({nb_obs_supprimees} observation(s) et {nb_suivi_supprimees} mesure(s) de suivi supprimée(s))"
        return True, msg
    except Exception as e:
        return False, f"❌ Erreur lors de la suppression : {e}"


# =============================================================================
# EXPORTS
# =============================================================================

def exporter_observations_excel(df_observations, df_equipements):
    """
    Génère un fichier Excel avec observations enrichies
    Format professionnel avec tableau Excel et formatage

    Args:
        df_observations (DataFrame): Observations filtrées
        df_equipements (DataFrame): Référentiel équipements

    Returns:
        BytesIO: Buffer contenant fichier Excel
    """
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    # Fusion
    df_export = df_observations.merge(
        df_equipements[['id_equipement', 'departement']],
        on='id_equipement',
        how='left'
    )

    # Colonnes export avec colonne vide après ID Equipement
    colonnes = [
        'departement', 'id_equipement', 'date',
        'observation', 'recommandation',
        'Travaux effectués & Notes', 'analyste', 'importance'
    ]

    df_export = df_export[colonnes].copy()

    # Renommage pour clarté
    df_export.columns = [
        'Département', 'ID Équipement', 'Date',
        'Observation', 'Recommandation',
        'Travaux effectués & Notes', 'Analyste', 'Importance'
    ]

    # Tri par date décroissante
    df_export = df_export.sort_values('Date', ascending=False)

    # Formatage de la date
    df_export['Date'] = pd.to_datetime(df_export['Date']).dt.strftime('%d/%m/%Y')

    # Conversion Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='Observations', index=False, startrow=0)

        worksheet = writer.sheets['Observations']

        # Style pour les en-têtes
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Style pour les bordures
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Style pour les cellules de données
        data_alignment = Alignment(vertical="top", wrap_text=True)

        # Appliquer le style aux en-têtes
        for col_num, column_title in enumerate(df_export.columns, 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = thin_border

        # Appliquer le style aux données
        for row_num in range(2, len(df_export) + 2):
            for col_num in range(1, len(df_export.columns) + 1):
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.alignment = data_alignment
                cell.border = thin_border

        # Ajustement des largeurs de colonnes
        column_widths = {
            'Département': 20,
            'ID Équipement': 15,
            'Date': 12,
            'Observation': 40,
            'Recommandation': 40,
            'Travaux effectués & Notes': 40,
            'Analyste': 15,
            'Importance': 25
        }

        for idx, col in enumerate(df_export.columns, 1):
            col_letter = get_column_letter(idx)
            worksheet.column_dimensions[col_letter].width = column_widths.get(col, 15)

        # Ajuster la hauteur des lignes pour le contenu
        for row in worksheet.iter_rows(min_row=2, max_row=len(df_export) + 1):
            max_lines = 1
            for cell in row:
                if cell.value:
                    lines = str(cell.value).count('\n') + 1
                    max_lines = max(max_lines, lines)
            worksheet.row_dimensions[row[0].row].height = max(15 * max_lines, 30)

        # Figer la première ligne (en-têtes)
        worksheet.freeze_panes = 'A2'

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