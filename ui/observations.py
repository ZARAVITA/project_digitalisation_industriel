"""
Onglet Observations - Saisie et consultation
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data.data_manager import (
    charger_equipements,
    charger_observations,
    sauvegarder_observation
)
def reset_saisie():
    for key in [
        "obs_input",
        "reco_input",
        "trav_input",
        "analyste_input"
    ]:
        if key in st.session_state:
            st.session_state[key] = ""

def render():
    """Affiche l'onglet Observations"""

    st.header("📝 Gestion des Observations")
    st.caption("Saisie rapide et consultation de l'historique")

    # Chargement données
    df_equipements = charger_equipements()
    df_observations = charger_observations()

    if df_equipements.empty:
        st.error("⚠️ Aucun équipement disponible. Configurez d'abord le référentiel.")
        return

    # =============================================================================
    # BLOC 1 : NOUVELLE OBSERVATION
    # =============================================================================

    with st.container(border=True):
        st.subheader("➕ Nouvelle observation")

        # Utilisation d'un formulaire pour UX fluide
        with st.form("form_observation", clear_on_submit=True):

            # Ligne 1 : Sélecteurs
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                departements = sorted(df_equipements['departement'].unique())
                dept_selectionne = st.selectbox(
                    "Département",
                    options=departements,
                    key="form_dept"
                )

            with col2:
                # Filtrage équipements par département
                equipements_dept = df_equipements[
                    df_equipements['departement'] == dept_selectionne
                    ]

                id_selectionne = st.selectbox(
                    "Équipement",
                    options=sorted(equipements_dept['id_equipement'].tolist()),
                    key="form_equip"
                )

            with col3:
                date_obs = st.date_input(
                    "Date",
                    value=datetime.now(),
                    key="form_date"
                )

            st.markdown("##")

            # Ligne 2 : Champs texte
            col_obs, col_reco, col_trav = st.columns(3)

            with col_obs:
                observation = st.text_area(
                    "Observation *",
                    height=120,
                    placeholder="Décrivez l'état constaté, anomalies...",
                    key="form_obs"
                )

            with col_reco:
                recommandation = st.text_area(
                    "Recommandation",
                    height=120,
                    placeholder="Actions à entreprendre, pièces à commander...",
                    key="form_reco"
                )

            with col_trav:
                travaux = st.text_area(
                    "Travaux effectués & Notes",
                    height=120,
                    placeholder="Travaux réalisés et remarques...",
                    key="form_trav"
                )

            st.markdown("##")

            # Ligne 3 : Analyste et bouton
            col_analyste, col_btn = st.columns([3, 1])

            with col_analyste:
                analyste = st.text_input(
                    "Analyste *",
                    placeholder="Nom de l'analyste",
                    key="form_analyste"
                )

            with col_btn:
                st.write("")  # Espacement vertical
                submitted = st.form_submit_button(
                    "✅ Enregistrer",
                    type="primary",
                    use_container_width=True
                )

            # Validation et enregistrement
            if submitted:
                # Validation champs requis
                if not observation.strip():
                    st.error("⚠️ L'observation est requise")
                elif not analyste.strip():
                    st.error("⚠️ Le nom de l'analyste est requis")
                else:
                    # Sauvegarde
                    success, message = sauvegarder_observation(
                        id_selectionne,
                        date_obs,
                        observation.strip(),
                        recommandation.strip(),
                        travaux.strip(),
                        analyste.strip()
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # =============================================================================
    # BLOC 2 : HISTORIQUE
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📋 Historique des observations")

        if df_observations.empty:
            st.info("ℹ️ Aucune observation enregistrée")
            return

        # Conversion dates
        df_obs = df_observations.copy()
        df_obs['date'] = pd.to_datetime(df_obs['date'], errors='coerce')

        # =============================================================================
        # FILTRES
        # =============================================================================

        col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1])

        with col_f1:
            dept_filter = st.multiselect(
                "Département(s)",
                options=sorted(df_equipements['departement'].unique()),
                default=None,
                placeholder="Tous"
            )

        with col_f2:
            # Équipements disponibles selon filtre département
            if dept_filter:
                equip_disponibles = df_equipements[
                    df_equipements['departement'].isin(dept_filter)
                ]['id_equipement'].tolist()
            else:
                equip_disponibles = df_equipements['id_equipement'].tolist()

            equip_filter = st.multiselect(
                "Équipement(s)",
                options=sorted(equip_disponibles),
                default=None,
                placeholder="Tous"
            )

        with col_f3:
            # Intervalle dates
            date_min = df_obs['date'].min().date()
            date_max = df_obs['date'].max().date()

            date_range = st.date_input(
                "Période",
                value=(date_min, date_max),
                min_value=date_min,
                max_value=date_max
            )

        # Application filtres
        df_filtered = df_obs.copy()

        if dept_filter:
            ids_dept = df_equipements[
                df_equipements['departement'].isin(dept_filter)
            ]['id_equipement'].tolist()
            df_filtered = df_filtered[df_filtered['id_equipement'].isin(ids_dept)]

        if equip_filter:
            df_filtered = df_filtered[df_filtered['id_equipement'].isin(equip_filter)]

        if len(date_range) == 2:
            start_date, end_date = date_range
            df_filtered = df_filtered[
                (df_filtered['date'].dt.date >= start_date) &
                (df_filtered['date'].dt.date <= end_date)
                ]

        # Fusion avec équipements
        df_display = df_filtered.merge(
            df_equipements[['id_equipement', 'departement']],
            on='id_equipement',
            how='left'
        )

        # Tri par date décroissante
        df_display = df_display.sort_values('date', ascending=False)

        # Formatage date
        df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d')

        with col_f4:
            st.metric(
                "Résultats",
                len(df_display)
            )

        st.markdown("##")

        # =============================================================================
        # TABLEAU
        # =============================================================================

        # Afficher seulement les 5 plus récentes par défaut si aucun filtre
        if not dept_filter and not equip_filter and len(date_range) == 2:
            if (date_range[0] == date_min and date_range[1] == date_max):
                st.caption("📌 Affichage des **5 observations les plus récentes**")
                df_display = df_display.head(5)

        st.dataframe(
            df_display[[
                'departement', 'id_equipement', 'date',
                'observation', 'recommandation',
                'Travaux effectués & Notes', 'analyste'
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                'departement': 'Département',
                'id_equipement': 'ID Équipement',
                'date': 'Date',
                'observation': st.column_config.TextColumn(
                    'Observation',
                    width='large'
                ),
                'recommandation': st.column_config.TextColumn(
                    'Recommandation',
                    width='large'
                ),
                'Travaux effectués & Notes': st.column_config.TextColumn(
                    'Travaux & Notes',
                    width='large'
                ),
                'analyste': 'Analyste'
            }
        )

        st.caption(f"**{len(df_display)}** observation(s) affichée(s)")