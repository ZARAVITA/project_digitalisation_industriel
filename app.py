"""
Application Streamlit - Gestion des Rapports de Maintenance
MVP destiné aux analystes techniques
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_DIR = "data"
EQUIPEMENTS_FILE = os.path.join(DATA_DIR, "equipements.xlsx")
OBSERVATIONS_FILE = os.path.join(DATA_DIR, "observations.csv")

# Colonnes attendues
EQUIPEMENTS_COLS = ["id_equipement", "departement"]
OBSERVATIONS_COLS = ["id_equipement", "date", "observation", "recommandation","Travaux effectués & Notes", "analyste"]


# =============================================================================
# FONCTIONS DE GESTION DES DONNÉES
# =============================================================================

def initialiser_fichiers():
    """Crée les fichiers de données s'ils n'existent pas"""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Initialiser équipements avec des données exemples
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


def charger_equipements():
    """Charge la liste des équipements depuis Excel"""
    try:
        df = pd.read_excel(EQUIPEMENTS_FILE)
        # Validation des colonnes
        if not all(col in df.columns for col in EQUIPEMENTS_COLS):
            st.error(f"⚠️ Colonnes manquantes dans {EQUIPEMENTS_FILE}")
            return pd.DataFrame(columns=EQUIPEMENTS_COLS)
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des équipements : {e}")
        return pd.DataFrame(columns=EQUIPEMENTS_COLS)


def charger_observations():
    """Charge l'historique des observations depuis CSV"""
    try:
        df = pd.read_csv(OBSERVATIONS_FILE, parse_dates=["date"])
        # Validation des colonnes
        if not all(col in df.columns for col in OBSERVATIONS_COLS):
            st.error(f"⚠️ Colonnes manquantes dans {OBSERVATIONS_FILE}")
            return pd.DataFrame(columns=OBSERVATIONS_COLS)
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des observations : {e}")
        return pd.DataFrame(columns=OBSERVATIONS_COLS)

def reset_saisie():
    for key in [
        "obs_input",
        "reco_input",
        "trav_input",
        "analyste_input"
    ]:
        if key in st.session_state:
            st.session_state[key] = ""

def sauvegarder_observation(id_equipement, date, observation, recommandation,trav_notes ,analyste):
    """
    Enregistre une nouvelle observation dans le fichier CSV

    Args:
        id_equipement (str): Identifiant de l'équipement
        date (datetime): Date de l'observation
        observation (str): Texte de l'observation
        recommandation (str): Texte de la recommandation
        trav_notes (str): Texte de la travaux&Notes
        analyste (str): Nom de l'analyste

    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Charger les observations existantes
        df_obs = charger_observations()

        # Créer nouvelle ligne
        nouvelle_obs = pd.DataFrame([{
            "id_equipement": id_equipement,
            "date": date.strftime("%Y-%m-%d"),
            "observation": observation,
            "recommandation": recommandation,
            "Travaux effectués & Notes": trav_notes,
            "analyste": analyste
        }])

        # Ajouter et sauvegarder
        df_obs = pd.concat([df_obs, nouvelle_obs], ignore_index=True)
        df_obs.to_csv(OBSERVATIONS_FILE, index=False)

        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de la sauvegarde : {e}")
        return False


def exporter_excel(df_equipements, df_observations):
    """
    Génère un fichier Excel avec les données complètes

    Args:
        df_equipements (DataFrame): Données des équipements
        df_observations (DataFrame): Données des observations

    Returns:
        BytesIO: Buffer contenant le fichier Excel
    """
    # Fusion des données
    df_export = df_observations.merge(
        df_equipements,
        on="id_equipement",
        how="left"
    )

    # Réorganisation des colonnes
    colonnes_export = [
        "departement",
        "id_equipement",
        "date",
        "observation",
        "recommandation",
        "Travaux effectués & Notes",
        "analyste"
    ]

    # Sélection et renommage
    df_export = df_export[colonnes_export]
    df_export.columns = [
        "Département",
        "ID Équipement",
        "Date",
        "Observation",
        "Recommandation",
        "Travaux effectués & Notes",
        "Analyste"
    ]

    # Tri par date décroissante
    df_export = df_export.sort_values("Date", ascending=False)

    # Conversion en Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_export.to_excel(writer, sheet_name="Rapport Maintenance", index=False)

        # Ajustement automatique de la largeur des colonnes
        worksheet = writer.sheets["Rapport Maintenance"]
        for idx, col in enumerate(df_export.columns):
            max_length = max(
                df_export[col].astype(str).map(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

    buffer.seek(0)
    return buffer


# =============================================================================
# INTERFACE STREAMLIT
# =============================================================================

def main():
    """Fonction principale de l'application"""

    # Configuration de la page
    st.set_page_config(
        page_title="Rapport Maintenance",
        page_icon="🔧",
        layout="wide"
    )

    # Initialisation
    initialiser_fichiers()

    # En-tête
    st.title("📊 Gestion des Rapports de Maintenance")
    st.markdown("---")

    # Chargement des données
    df_equipements = charger_equipements()
    df_observations = charger_observations()

    if df_equipements.empty:
        st.warning("⚠️ Aucun équipement trouvé. Veuillez configurer le fichier equipements.xlsx")
        return

    # =============================================================================
    # SECTION SAISIE
    # =============================================================================

    st.header("📝 Nouvelle observation")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        # Sélection département
        departements = sorted(df_equipements["departement"].unique())
        departement_selectionne = st.selectbox(
            "Département",
            options=departements,
            key="dept_select",
            on_change=reset_saisie
        )

    with col2:
        # Sélection équipement (filtré par département)
        equipements_filtres = df_equipements[
            df_equipements["departement"] == departement_selectionne
            ]

        equipement_options = {
            f"{row['id_equipement']}": row["id_equipement"]
            for _, row in equipements_filtres.iterrows()
        }

        equipement_selectionne_label = st.selectbox(
            "Équipement",
            options=list(equipement_options.keys()),
            key="equip_select",
            on_change=reset_saisie
        )
        equipement_selectionne_id = equipement_options[equipement_selectionne_label]

    with col3:
        # Sélection date
        date_observation = st.date_input(
            "Date",
            value=datetime.now(),
            key="date_select"
        )

    # Champs de saisie
    col_obs, col_reco, col_trav = st.columns(3)

    with col_obs:
        observation = st.text_area(
            "Observation",
            height=150,
            placeholder="Décrivez l'état constaté, les anomalies observées...",
            key="obs_input"
        )

    with col_reco:
        recommandation = st.text_area(
            "Recommandation",
            height=150,
            placeholder="Actions à entreprendre, pièces à commander...",
            key="reco_input"
        )
    with col_trav:
        trav_notes = st.text_area(
            "Travaux effectués & Notes",
            height=150,
            placeholder="Les travaux que vous avez effectuées et vos notes",
            key="trav_input"
        )

    # Nom analyste
    col_analyste, col_btn = st.columns([3, 1])

    with col_analyste:
        analyste = st.text_input(
            "Analyste",
            placeholder="Nom de l'analyste",
            key="analyste_input"
        )

    with col_btn:
        st.write("")  # Espacement
        st.write("")
        enregistrer = st.button("✅ Enregistrer", type="primary", use_container_width=True)

    # Validation et enregistrement
    if enregistrer:
        if not observation.strip():
            st.error("⚠️ L'observation ne peut pas être vide")
        elif not analyste.strip():
            st.error("⚠️ Le nom de l'analyste est requis")
        else:
            if sauvegarder_observation(
                    equipement_selectionne_id,
                    date_observation,
                    observation.strip(),
                    recommandation.strip(),
                    trav_notes.strip(),
                    analyste.strip()
            ):
                st.success("✅ Observation enregistrée avec succès")
                st.rerun()

    st.markdown("---")

    # =============================================================================
    # SECTION CONSULTATION
    # =============================================================================

    st.header("📋 Historique des Observations")

    if df_observations.empty:
        st.info("ℹ️ Aucune observation enregistrée pour le moment")
    else:
        df_obs = df_observations.copy()
        df_obs["date"] = pd.to_datetime(
            df_obs["date"],
            format="mixed",
            errors="coerce"
        )
        # Filtres
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            dept_filter = st.multiselect(
                "Filtrer par département",
                options=sorted(df_equipements["departement"].unique()),
                default=None
            )

        with col_filter2:
            if dept_filter:
                equip_disponibles = df_equipements[
                    df_equipements["departement"].isin(dept_filter)
                ]["id_equipement"].tolist()
            else:
                equip_disponibles = df_equipements["id_equipement"].tolist()

            equip_filter = st.multiselect(
                "Filtrer par équipement",
                options=sorted(equip_disponibles),
                default=None
            )

        with col_filter3:
            date_min_data = df_obs["date"].min()
            date_max_data = df_obs["date"].max()
            min_date = date_min_data.date()
            max_date = date_max_data.date()
            date_filter = st.date_input(
                "Filtrer par date",
                value=(date_min_data.date(), date_max_data.date()),
                min_value=min_date,  # borne UX large
                max_value=max_date
            )
        # Application des filtres
        df_filtered = df_obs.copy()


        if dept_filter:
            ids_dept = df_equipements[
                df_equipements["departement"].isin(dept_filter)
            ]["id_equipement"].tolist()
            df_filtered = df_filtered[df_filtered["id_equipement"].isin(ids_dept)]

        if equip_filter:
            df_filtered = df_filtered[df_filtered["id_equipement"].isin(equip_filter)]
        if len(date_filter) == 2:
            start_date, end_date = date_filter
            df_filtered = df_filtered[
                (df_filtered["date"].dt.date >= start_date) &
                (df_filtered["date"].dt.date <= end_date)
                ]

        # Fusion avec équipements pour affichage
        df_display = df_filtered.merge(
            df_equipements[["id_equipement", "departement"]],
            on="id_equipement",
            how="left"
        )

        # Tri par date décroissante
        df_display = df_display.sort_values("date", ascending=False)

        # Reformatage des dates
        df_display["date"] = (
            pd.to_datetime(df_display["date"], format="mixed", errors="coerce")
            .dt.strftime("%Y-%m-%d")
        )

        # Affichage
        st.dataframe(
            df_display[[
                "departement", "id_equipement",
                "date", "observation", "recommandation","Travaux effectués & Notes", "analyste"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "departement": "Département",
                "id_equipement": "ID",
                "date": "Date",
                "observation": st.column_config.TextColumn("Observation", width="large"),
                "recommandation": st.column_config.TextColumn("Recommandation", width="large"),
                "trav_notes": st.column_config.TextColumn("Travaux effectués & Notes", width="large"),
                "analyste": "Analyste"
            }
        )

        st.caption(f"**{len(df_display)}** observation(s) affichée(s)")

    st.markdown("---")

    # =============================================================================
    # SECTION EXPORT
    # =============================================================================

    st.header("📥 Export Excel")

    col_export1, col_export2, col_export3 = st.columns([2, 1, 1])

    with col_export1:
        st.write("Téléchargez l'intégralité des observations au format Excel")

    with col_export3:
        if not df_observations.empty:
            fichier_excel = exporter_excel(df_equipements, df_observations)
            nom_fichier = f"rapport_maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            st.download_button(
                label="📥 Télécharger Excel",
                data=fichier_excel,
                file_name=nom_fichier,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.button("📥 Télécharger Excel", disabled=True, use_container_width=True)
            st.caption("Aucune donnée à exporter")


if __name__ == "__main__":
    main()