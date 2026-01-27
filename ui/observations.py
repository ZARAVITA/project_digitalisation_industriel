"""
Onglet Observations - Saisie et consultation
Inclut: gestion observations, saisie suivi équipements, visualisation graphique
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from data.data_manager import (
    charger_equipements,
    charger_observations,
    sauvegarder_observation,
    charger_suivi,
    sauvegarder_suivi,
    OPTIONS_IMPORTANCE,
    POINTS_MESURE
)


def render():
    """Affiche l'onglet Observations avec ses 4 sections"""

    st.header("📝 Gestion des Observations & Suivi")
    st.caption("Saisie rapide, suivi technique et visualisation graphique")

    # Chargement données
    df_equipements = charger_equipements()
    df_observations = charger_observations()
    df_suivi = charger_suivi()

    if df_equipements.empty:
        st.error("⚠️ Aucun équipement disponible. Configurez d'abord le référentiel.")
        return

    # =============================================================================
    # BLOC 1 : NOUVELLE OBSERVATION
    # =============================================================================

    with st.container(border=True):
        st.subheader("➕ Nouvelle observation")

        # Sélection du département HORS du formulaire
        departements = sorted(df_equipements['departement'].unique())
        dept_selectionne = st.selectbox(
            "1️⃣ Département",
            options=departements,
            key="dept_select_obs"
        )

        # Filtrage équipements par département
        equipements_dept = df_equipements[
            df_equipements['departement'] == dept_selectionne
        ]

        # Formulaire
        with st.form("form_observation", clear_on_submit=True):

            # Ligne 1 : Sélecteurs
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                id_selectionne = st.selectbox(
                    "2️⃣ Équipement",
                    options=sorted(equipements_dept['id_equipement'].tolist()),
                    key="form_equip"
                )

            with col2:
                date_obs = st.date_input(
                    "3️⃣ Date",
                    value=datetime.now(),
                    key="form_date"
                )

            with col3:
                importance = st.selectbox(
                    "4️⃣ Importance",
                    options=OPTIONS_IMPORTANCE,
                    key="form_importance"
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
                        analyste.strip(),
                        importance
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # =============================================================================
    # BLOC 2 : SAISIE DONNÉES DE SUIVI
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📊 Saisie des mesures de suivi")
        st.caption("Enregistrement des données vibratoires et de vitesse")

        # Sélection du département HORS du formulaire
        dept_suivi = st.selectbox(
            "1️⃣ Département",
            options=departements,
            key="dept_select_suivi"
        )

        # Filtrage équipements par département
        equipements_dept_suivi = df_equipements[
            df_equipements['departement'] == dept_suivi
        ]

        # Formulaire de saisie
        with st.form("form_suivi", clear_on_submit=True):

            # Ligne 1 : Sélecteurs principaux
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                id_suivi = st.selectbox(
                    "2️⃣ Équipement",
                    options=sorted(equipements_dept_suivi['id_equipement'].tolist()),
                    key="form_suivi_equip"
                )

            with col2:
                point_mesure = st.selectbox(
                    "3️⃣ Point de mesure",
                    options=POINTS_MESURE,
                    key="form_suivi_point"
                )

            with col3:
                date_suivi = st.date_input(
                    "4️⃣ Date",
                    value=datetime.now(),
                    key="form_suivi_date"
                )

            st.markdown("##")

            # Ligne 2 : Mesures numériques
            col_v, col_twf, col_crest, col_peak = st.columns(4)

            with col_v:
                vitesse_rpm = st.number_input(
                    "Vitesse (RPM) *",
                    min_value=0.0,
                    max_value=10000.0,
                    value=0.0,
                    step=10.0,
                    format="%.2f",
                    key="form_suivi_vitesse"
                )

            with col_twf:
                twf_rms_g = st.number_input(
                    "TWF RMS (g) *",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="form_suivi_twf_rms"
                )

            with col_crest:
                crest_factor = st.number_input(
                    "CREST FACTOR *",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.1,
                    format="%.2f",
                    key="form_suivi_crest"
                )

            with col_peak:
                twf_peak = st.number_input(
                    "TWF Peak to Peak (g) *",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="form_suivi_peak"
                )

            st.markdown("##")

            # Bouton de soumission
            col_info, col_btn_suivi = st.columns([3, 1])

            with col_info:
                st.caption("📌 Tous les champs sont requis pour la saisie")

            with col_btn_suivi:
                submitted_suivi = st.form_submit_button(
                    "✅ Enregistrer mesure",
                    type="primary",
                    use_container_width=True
                )

            # Validation et enregistrement
            if submitted_suivi:
                # Validation: au moins une valeur non nulle
                if vitesse_rpm == 0.0 and twf_rms_g == 0.0 and crest_factor == 0.0 and twf_peak == 0.0:
                    st.error("⚠️ Au moins une mesure doit être différente de zéro")
                else:
                    # Sauvegarde
                    success, message = sauvegarder_suivi(
                        id_suivi,
                        point_mesure,
                        date_suivi,
                        vitesse_rpm,
                        twf_rms_g,
                        crest_factor,
                        twf_peak
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # =============================================================================
    # BLOC 3 : VISUALISATION GRAPHIQUE
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📈 Visualisation des tendances")
        st.caption("Analyse temporelle des mesures de suivi")

        if df_suivi.empty:
            st.info("ℹ️ Aucune donnée de suivi enregistrée pour le moment")
        else:
            # Filtres pour la visualisation
            col_f1, col_f2, col_f3 = st.columns([2, 2, 2])

            with col_f1:
                # Liste des équipements ayant des données de suivi
                equips_avec_suivi = sorted(df_suivi['id_equipement'].unique())
                equip_graph = st.selectbox(
                    "Équipement",
                    options=equips_avec_suivi,
                    key="graph_equip"
                )

            with col_f2:
                # Points de mesure disponibles pour cet équipement
                points_disponibles = sorted(
                    df_suivi[df_suivi['id_equipement'] == equip_graph]['point_mesure'].unique()
                )
                point_graph = st.selectbox(
                    "Point de mesure",
                    options=points_disponibles,
                    key="graph_point"
                )

            with col_f3:
                # Variables à visualiser
                variables_disponibles = {
                    "Vitesse (RPM)": "vitesse_rpm",
                    "TWF RMS (g)": "twf_rms_g",
                    "CREST FACTOR": "crest_factor",
                    "TWF Peak to Peak (g)": "twf_peak_to_peak_g"
                }
                variable_graph = st.selectbox(
                    "Variable à afficher",
                    options=list(variables_disponibles.keys()),
                    key="graph_variable"
                )

            # Filtrage des données
            df_graph = df_suivi[
                (df_suivi['id_equipement'] == equip_graph) &
                (df_suivi['point_mesure'] == point_graph)
            ].copy()

            df_graph = df_graph.sort_values('date')

            if df_graph.empty:
                st.warning(f"⚠️ Aucune donnée pour {equip_graph} - {point_graph}")
            else:
                # Création du graphique
                variable_col = variables_disponibles[variable_graph]

                fig = px.line(
                    df_graph,
                    x='date',
                    y=variable_col,
                    markers=True,
                    title=f"{variable_graph} - {equip_graph} ({point_graph})"
                )

                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title=variable_graph,
                    hovermode='x unified',
                    height=400,
                    showlegend=False
                )

                fig.update_traces(
                    line=dict(color='#366092', width=2),
                    marker=dict(size=8, color='#366092')
                )

                st.plotly_chart(fig, use_container_width=True)

                # Statistiques rapides
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

                with col_stat1:
                    st.metric("Minimum", f"{df_graph[variable_col].min():.2f}")

                with col_stat2:
                    st.metric("Maximum", f"{df_graph[variable_col].max():.2f}")

                with col_stat3:
                    st.metric("Moyenne", f"{df_graph[variable_col].mean():.2f}")

                with col_stat4:
                    st.metric("Dernière valeur", f"{df_graph[variable_col].iloc[-1]:.2f}")

    # =============================================================================
    # BLOC 4 : HISTORIQUE DES OBSERVATIONS
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

        # Filtres
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
        df_display['date'] = df_display['date'].dt.strftime('%d/%m/%Y')

        with col_f4:
            st.metric(
                "Résultats",
                len(df_display)
            )

        st.markdown("##")

        # Afficher seulement les 5 plus récentes par défaut si aucun filtre
        if not dept_filter and not equip_filter and len(date_range) == 2:
            if (date_range[0] == date_min and date_range[1] == date_max):
                st.caption("📌 Affichage des **5 observations les plus récentes**")
                df_display = df_display.head(5)

        st.dataframe(
            df_display[[
                'departement', 'id_equipement', 'date',
                'observation', 'recommandation',
                'Travaux effectués & Notes', 'analyste', 'importance'
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
                'analyste': 'Analyste',
                'importance': st.column_config.TextColumn(
                    'Importance',
                    width='medium'
                )
            }
        )

        st.caption(f"**{len(df_display)}** observation(s) affichée(s)")