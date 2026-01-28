"""
Onglet Observations - Saisie et consultation avec visualisation des tendances
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data.data_manager import (
    charger_equipements,
    charger_observations,
    charger_suivi,
    sauvegarder_observation
)


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
            col1, col2 = st.columns([2, 1])

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

        # FILTRES
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

        # TABLEAU
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

    # =============================================================================
    # BLOC 3 : VISUALISATION DES TENDANCES
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📈 Visualisation des tendances")

        # Charger les données de suivi
        df_suivi = charger_suivi()

        if df_suivi.empty:
            st.info("ℹ️ Aucune donnée de suivi disponible")
            return

        # Conversion dates
        df_suivi['date'] = pd.to_datetime(df_suivi['date'], errors='coerce')

        # FILTRES
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            # Filtre ID équipement
            id_equip_suivi = st.selectbox(
                "ID Équipement",
                options=sorted(df_suivi['id_equipement'].unique()),
                key="id_equip_tendances"
            )

        with col_f2:
            # Filtre point de mesure
            df_equip_suivi = df_suivi[df_suivi['id_equipement'] == id_equip_suivi]
            point_mesure_suivi = st.selectbox(
                "Point de mesure",
                options=sorted(df_equip_suivi['point_mesure'].unique()),
                key="point_mesure_tendances"
            )

        # Filtrer les données
        df_filtered_suivi = df_suivi[
            (df_suivi['id_equipement'] == id_equip_suivi) &
            (df_suivi['point_mesure'] == point_mesure_suivi)
        ].copy()

        if df_filtered_suivi.empty:
            st.warning("⚠️ Aucune donnée pour cette sélection")
            return

        # Trier par date
        df_filtered_suivi = df_filtered_suivi.sort_values('date')

        st.markdown("##")

        # FILTRES TEMPORELS
        col_t1, col_t2, col_t3 = st.columns([2, 2, 1])

        with col_t1:
            # Mode de filtrage
            mode_filtrage = st.radio(
                "Mode de filtrage",
                options=["Période personnalisée", "22 dernières observations"],
                horizontal=True,
                key="mode_filtrage_tendances"
            )

        if mode_filtrage == "Période personnalisée":
            with col_t2:
                date_min_suivi = df_filtered_suivi['date'].min().date()
                date_max_suivi = df_filtered_suivi['date'].max().date()

                date_debut_suivi = st.date_input(
                    "Date début",
                    value=date_min_suivi,
                    min_value=date_min_suivi,
                    max_value=date_max_suivi,
                    key="date_debut_tendances"
                )

            with col_t3:
                date_fin_suivi = st.date_input(
                    "Date fin",
                    value=date_max_suivi,
                    min_value=date_min_suivi,
                    max_value=date_max_suivi,
                    key="date_fin_tendances"
                )

            # Appliquer le filtre de dates
            df_filtered_suivi = df_filtered_suivi[
                (df_filtered_suivi['date'].dt.date >= date_debut_suivi) &
                (df_filtered_suivi['date'].dt.date <= date_fin_suivi)
            ]
        else:
            # Prendre les 22 dernières observations (ou moins si insuffisant)
            df_filtered_suivi = df_filtered_suivi.tail(22)

        st.markdown("##")

        # SÉLECTION DES VARIABLES
        variables_disponibles = {
            'vitesse_rpm': 'Vitesse (RPM)',
            'twf_rms_g': 'TWF RMS (g)',
            'crest_factor': 'Crest Factor',
            'twf_peak_to_peak_g': 'TWF Peak-to-Peak (g)'
        }

        variables_selectionnees = st.multiselect(
            "Variables à afficher",
            options=list(variables_disponibles.keys()),
            default=['twf_rms_g'],
            format_func=lambda x: variables_disponibles[x],
            key="variables_tendances"
        )

        if not variables_selectionnees:
            st.warning("⚠️ Veuillez sélectionner au moins une variable")
            return

        st.markdown("##")

        # CRÉATION DU GRAPHIQUE
        fig = go.Figure()

        # Palette de couleurs
        couleurs = {
            'vitesse_rpm': '#1f77b4',
            'twf_rms_g': '#ff7f0e',
            'crest_factor': '#2ca02c',
            'twf_peak_to_peak_g': '#d62728'
        }

        for var in variables_selectionnees:
            fig.add_trace(go.Scatter(
                x=df_filtered_suivi['date'],
                y=df_filtered_suivi[var],
                mode='lines+markers',
                name=variables_disponibles[var],
                line=dict(color=couleurs[var], width=2),
                marker=dict(size=6)
            ))

        # Mise en forme
        fig.update_layout(
            title=f"Tendances - {id_equip_suivi} - {point_mesure_suivi}",
            xaxis_title="Date",
            yaxis_title="Valeurs",
            hovermode='x unified',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Statistiques
        st.markdown("##")
        st.caption(f"**{len(df_filtered_suivi)}** mesure(s) affichée(s)")

        # Tableau récapitulatif
        with st.expander("📊 Statistiques détaillées"):
            stats_data = []
            for var in variables_selectionnees:
                stats_data.append({
                    'Variable': variables_disponibles[var],
                    'Minimum': f"{df_filtered_suivi[var].min():.2f}",
                    'Maximum': f"{df_filtered_suivi[var].max():.2f}",
                    'Moyenne': f"{df_filtered_suivi[var].mean():.2f}",
                    'Écart-type': f"{df_filtered_suivi[var].std():.2f}"
                })

            st.dataframe(
                pd.DataFrame(stats_data),
                use_container_width=True,
                hide_index=True
            )