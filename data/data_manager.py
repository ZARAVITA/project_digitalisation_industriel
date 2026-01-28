"""
Module de gestion des données (Excel/CSV)
Prêt pour migration future vers Supabase
"""

import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart.series import SeriesLabel
# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_DIR = "data"
EQUIPEMENTS_FILE = os.path.join(DATA_DIR, "equipements.xlsx")
OBSERVATIONS_FILE = os.path.join(DATA_DIR, "observations.csv")
SUIVI_FILE = os.path.join(DATA_DIR, "suivi_equipements_enrichi.csv")

# Schéma des données
EQUIPEMENTS_COLS = ["id_equipement", "departement"]
OBSERVATIONS_COLS = [
    "id_equipement", "date", "observation",
    "recommandation", "Travaux effectués & Notes", "analyste"
]
SUIVI_COLS = [
    "id_equipement", "point_mesure", "date",
    "vitesse_rpm", "twf_rms_g", "crest_factor", "twf_peak_to_peak_g"
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


def charger_suivi():
    """
    Charge les données de suivi des équipements depuis CSV

    Returns:
        DataFrame: Données de suivi avec dates parsées
    """
    try:
        df = pd.read_csv(SUIVI_FILE, parse_dates=["date"], encoding='utf-8')
        if not all(col in df.columns for col in SUIVI_COLS):
            raise ValueError(f"Colonnes manquantes dans {SUIVI_FILE}")
        return df
    except Exception as e:
        print(f"Erreur chargement suivi: {e}")
        return pd.DataFrame(columns=SUIVI_COLS)


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
            "date": pd.to_datetime(date),
            "observation": observation,
            "recommandation": recommandation,
            "Travaux effectués & Notes": trav_notes,
            "analyste": analyste
        }])

        df_obs['date'] = pd.to_datetime(df_obs['date'])

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


def supprimer_suivi(id_equipement, point_mesure, date):
    """
    Supprime une entrée de suivi spécifique

    Args:
        id_equipement (str): ID équipement
        point_mesure (str): Point de mesure
        date (datetime.date): Date du suivi

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        df_suivi = charger_suivi()

        # Convertir date pour comparaison
        df_suivi['date'] = pd.to_datetime(df_suivi['date']).dt.date
        date_cible = pd.to_datetime(date).date()

        # Vérifier existence
        mask = (
            (df_suivi['id_equipement'] == id_equipement) &
            (df_suivi['point_mesure'] == point_mesure) &
            (df_suivi['date'] == date_cible)
        )

        if not mask.any():
            return False, "⚠️ Aucun suivi trouvé pour ces critères"

        # Supprimer
        df_suivi = df_suivi[~mask]

        # Reconvertir en datetime avant sauvegarde
        df_suivi['date'] = pd.to_datetime(df_suivi['date'])
        df_suivi.to_csv(SUIVI_FILE, index=False, encoding='utf-8')

        return True, "✅ Suivi supprimé avec succès"
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



def exporter_suivi_excel(df_suivi, df_equipements):
    """
    Génère un fichier Excel professionnel avec suivi de mesures
    - Un onglet par ID équipement
    - Tableaux de données + graphique interactif avec double menu déroulant
    """
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import LineChart, Reference
    from openpyxl.chart.series import SeriesLabel
    from openpyxl.worksheet.datavalidation import DataValidation

    buffer = BytesIO()

    # Fusion avec départements
    df_export = df_suivi.merge(
        df_equipements[['id_equipement', 'departement']],
        on='id_equipement',
        how='left'
    )

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:

        for id_equip in sorted(df_export['id_equipement'].unique()):
            df_equip = df_export[df_export['id_equipement'] == id_equip].copy()
            sheet_name = id_equip[:31]

            df_equip_sorted = df_equip.sort_values(['point_mesure', 'date'])

            df_equip_sorted.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False,
                startrow=0
            )

            worksheet = writer.sheets[sheet_name]

            # =========================================================
            # === PRO TABLE STYLE (TABLEAU UNIQUEMENT)
            # =========================================================

            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=11)
            header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            data_alignment = Alignment(vertical="top", wrap_text=True)

            n_rows = len(df_equip_sorted)
            n_cols = len(df_equip_sorted.columns)

            # En-têtes
            for col_idx, col_name in enumerate(df_equip_sorted.columns, 1):
                cell = worksheet.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = thin_border

            # Données
            for row_idx in range(2, n_rows + 2):
                for col_idx in range(1, n_cols + 1):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    cell.alignment = data_alignment
                    cell.border = thin_border

            # === FORMAT DATE EXCEL (DD/MM/YYYY) ===
            if 'date' in df_equip_sorted.columns:
                date_col_idx = df_equip_sorted.columns.get_loc('date') + 1
                date_col_letter = get_column_letter(date_col_idx)

                for row_idx in range(2, n_rows + 2):
                    cell = worksheet[f"{date_col_letter}{row_idx}"]
                    cell.number_format = 'DD/MM/YYYY'

            # Largeur des colonnes (maîtrisée)
            for col_idx, col_name in enumerate(df_equip_sorted.columns, 1):
                col_letter = get_column_letter(col_idx)
                max_len = max(
                    df_equip_sorted[col_name].astype(str).map(len).max(),
                    len(col_name)
                )
                worksheet.column_dimensions[col_letter].width = min(max_len + 2, 22)

            # Hauteur des lignes (contenu multi-lignes)
            for row in worksheet.iter_rows(min_row=2, max_row=n_rows + 1):
                max_lines = 1
                for cell in row:
                    if cell.value:
                        max_lines = max(max_lines, str(cell.value).count('\n') + 1)
                worksheet.row_dimensions[row[0].row].height = max(18 * max_lines, 30)

            # Figer la ligne d'en-tête
            worksheet.freeze_panes = "A2"

            # =========================================================
            # === PARTIE GRAPHIQUE AVEC DOUBLE MENU DÉROULANT
            # =========================================================

            points_mesure = sorted(df_equip_sorted['point_mesure'].unique())

            if len(points_mesure) == 0:
                continue

            # Position de départ pour la zone interactive
            row_offset = n_rows + 4
            col_offset = 10  # Colonne J

            # === 1. CRÉER LA LISTE DES POINTS DE MESURE (cachée) ===
            list_pm_start_row = row_offset
            for idx, pm in enumerate(points_mesure):
                worksheet.cell(row=list_pm_start_row + idx, column=col_offset + 15, value=pm)

            # === 2. CRÉER LA LISTE DES MÉTRIQUES (cachée) ===
            metric_names = {
                'vitesse_rpm': 'Vitesse (RPM)',
                'twf_rms_g': 'TWF RMS (g)',
                'crest_factor': 'Crest Factor',
                'twf_peak_to_peak_g': 'TWF Peak-to-Peak (g)'
            }
            metric_columns = list(metric_names.keys())

            list_metric_start_row = row_offset
            for idx, (metric_key, metric_label) in enumerate(metric_names.items()):
                worksheet.cell(row=list_metric_start_row + idx, column=col_offset + 16, value=metric_label)

            # === 3. MENU DÉROULANT 1 : POINT DE MESURE ===
            label_pm_cell = worksheet.cell(row=row_offset, column=col_offset)
            label_pm_cell.value = "Point de mesure :"
            label_pm_cell.font = Font(bold=True, size=11)
            label_pm_cell.alignment = Alignment(horizontal="right", vertical="center")

            dropdown_pm_cell = worksheet.cell(row=row_offset, column=col_offset + 1)
            dropdown_pm_cell.value = points_mesure[0]
            dropdown_pm_cell.font = Font(size=11)
            dropdown_pm_cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
            dropdown_pm_cell.border = thin_border

            # Validation pour point de mesure
            list_pm_range = f"${get_column_letter(col_offset + 15)}${list_pm_start_row}:${get_column_letter(col_offset + 15)}${list_pm_start_row + len(points_mesure) - 1}"
            dv_pm = DataValidation(type="list", formula1=list_pm_range, allow_blank=False)
            dv_pm.error = 'Sélectionnez un point de mesure valide'
            dv_pm.errorTitle = 'Entrée invalide'
            worksheet.add_data_validation(dv_pm)
            dv_pm.add(dropdown_pm_cell)

            # === 4. MENU DÉROULANT 2 : MÉTRIQUE ===
            label_metric_cell = worksheet.cell(row=row_offset + 1, column=col_offset)
            label_metric_cell.value = "Métrique :"
            label_metric_cell.font = Font(bold=True, size=11)
            label_metric_cell.alignment = Alignment(horizontal="right", vertical="center")

            dropdown_metric_cell = worksheet.cell(row=row_offset + 1, column=col_offset + 1)
            dropdown_metric_cell.value = list(metric_names.values())[0]  # Première métrique par défaut
            dropdown_metric_cell.font = Font(size=11)
            dropdown_metric_cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
            dropdown_metric_cell.border = thin_border

            # Validation pour métrique
            list_metric_range = f"${get_column_letter(col_offset + 16)}${list_metric_start_row}:${get_column_letter(col_offset + 16)}${list_metric_start_row + len(metric_names) - 1}"
            dv_metric = DataValidation(type="list", formula1=list_metric_range, allow_blank=False)
            dv_metric.error = 'Sélectionnez une métrique valide'
            dv_metric.errorTitle = 'Entrée invalide'
            worksheet.add_data_validation(dv_metric)
            dv_metric.add(dropdown_metric_cell)

            # === 5. ZONE DE DONNÉES FILTRÉES ===
            filter_start_row = row_offset + 4
            pm_col_idx = df_equip_sorted.columns.get_loc('point_mesure') + 1
            date_col_idx = df_equip_sorted.columns.get_loc('date') + 1

            # Références aux cellules de menu déroulant
            dropdown_pm_ref = f"${get_column_letter(col_offset + 1)}${row_offset}"
            dropdown_metric_ref = f"${get_column_letter(col_offset + 1)}${row_offset + 1}"

            # En-têtes
            worksheet.cell(row=filter_start_row, column=col_offset).value = "Date"
            worksheet.cell(row=filter_start_row, column=col_offset).font = Font(bold=True)
            worksheet.cell(row=filter_start_row, column=col_offset).fill = PatternFill(start_color="D9E1F2",
                                                                                       end_color="D9E1F2",
                                                                                       fill_type="solid")

            worksheet.cell(row=filter_start_row, column=col_offset + 1).value = "Valeur"
            worksheet.cell(row=filter_start_row, column=col_offset + 1).font = Font(bold=True)
            worksheet.cell(row=filter_start_row, column=col_offset + 1).fill = PatternFill(start_color="D9E1F2",
                                                                                           end_color="D9E1F2",
                                                                                           fill_type="solid")

            # Colonnes des métriques dans les données source
            metric_col_indices = {
                metric: df_equip_sorted.columns.get_loc(metric) + 1
                for metric in metric_columns
            }

            # Formules dynamiques : filtrage par point de mesure ET sélection de la métrique
            for data_row_idx in range(filter_start_row + 1, filter_start_row + n_rows + 1):
                source_row = data_row_idx - filter_start_row + 1

                # Colonne Date
                date_formula = f'=IF(${get_column_letter(pm_col_idx)}{source_row}={dropdown_pm_ref},${get_column_letter(date_col_idx)}{source_row},NA())'
                worksheet.cell(row=data_row_idx, column=col_offset).value = date_formula
                worksheet.cell(row=data_row_idx, column=col_offset).number_format = 'DD/MM/YYYY'

                # Colonne Valeur (avec choix de métrique dynamique)
                # Utiliser des IF imbriqués pour sélectionner la bonne colonne selon la métrique choisie
                value_formula = f'=IF(${get_column_letter(pm_col_idx)}{source_row}={dropdown_pm_ref},'

                # Construction de la formule IF imbriquée pour chaque métrique
                for idx, (metric_key, metric_label) in enumerate(metric_names.items()):
                    if idx == 0:
                        value_formula += f'IF({dropdown_metric_ref}="{metric_label}",${get_column_letter(metric_col_indices[metric_key])}{source_row},'
                    elif idx < len(metric_names) - 1:
                        value_formula += f'IF({dropdown_metric_ref}="{metric_label}",${get_column_letter(metric_col_indices[metric_key])}{source_row},'
                    else:
                        # Dernière métrique (pas de IF supplémentaire)
                        value_formula += f'IF({dropdown_metric_ref}="{metric_label}",${get_column_letter(metric_col_indices[metric_key])}{source_row},NA())'

                # Fermer tous les IF
                value_formula += ')' * (len(metric_names) - 1) + ',NA())'

                worksheet.cell(row=data_row_idx, column=col_offset + 1).value = value_formula

            # === 6. CRÉER LE GRAPHIQUE ===
            chart = LineChart()
            chart.title = "Évolution temporelle"
            chart.style = 10
            chart.width = 20
            chart.height = 12

            # Axes
            chart.x_axis.title = "Date"
            chart.y_axis.title = "Valeur"
            chart.x_axis.number_format = 'dd/mm/yyyy'

            # Données du graphique (une seule série)
            values = Reference(
                worksheet,
                min_col=col_offset + 1,
                min_row=filter_start_row,
                max_row=filter_start_row + n_rows
            )
            chart.add_data(values, titles_from_data=True)

            # Dates en abscisse
            dates = Reference(
                worksheet,
                min_col=col_offset,
                min_row=filter_start_row + 1,
                max_row=filter_start_row + n_rows
            )
            chart.set_categories(dates)

            # Supprimer la légende (une seule série)
            chart.legend = None

            # Position du graphique
            chart_position = f"{get_column_letter(col_offset)}{row_offset + 7}"
            worksheet.add_chart(chart, chart_position)

            # Masquer les colonnes avec les listes
            worksheet.column_dimensions[get_column_letter(col_offset + 15)].hidden = True
            worksheet.column_dimensions[get_column_letter(col_offset + 16)].hidden = True

    buffer.seek(0)
    return buffer
