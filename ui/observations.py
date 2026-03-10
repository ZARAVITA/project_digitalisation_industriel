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
    sauvegarder_observation,
    sauvegarder_suivi
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

        departements = sorted(df_equipements['departement'].unique())
        dept_selectionne = st.selectbox(
            "1️⃣ Département",
            options=departements,
            key="dept_select_obs"
        )

        equipements_dept = df_equipements[
            df_equipements['departement'] == dept_selectionne
        ]

        with st.form("form_observation", clear_on_submit=True):

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
                    min_value=datetime(1990, 1, 1).date(),
                    max_value=datetime(2099, 12, 31).date(),
                    key="form_date"
                )

            st.markdown("##")

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

            col_analyste, col_importance, col_btn = st.columns([2, 2, 1])

            with col_analyste:
                analyste = st.text_input(
                    "Analyste *",
                    placeholder="Nom de l'analyste",
                    key="form_analyste"
                )

            with col_importance:
                importance_options = [
                    "",
                    "Très important",
                    "Important",
                    "Moins important",
                    "Pas de collecte mais important",
                    "Collecte réalisée"
                ]
                importance = st.selectbox(
                    "Importance",
                    options=importance_options,
                    key="form_importance",
                    help="Sélectionnez le niveau d'importance (optionnel)"
                )

            with col_btn:
                st.write("")
                submitted = st.form_submit_button(
                    "✅ Enregistrer",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                if not observation.strip():
                    st.error("⚠️ L'observation est requise")
                elif not analyste.strip():
                    st.error("⚠️ Le nom de l'analyste est requis")
                else:
                    success, message = sauvegarder_observation(
                        id_selectionne,
                        date_obs,
                        observation.strip(),
                        recommandation.strip(),
                        travaux.strip(),
                        analyste.strip(),
                        importance if importance else None
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

        df_suivi = charger_suivi()

        POINTS_MESURE = [
            "M-COA", "M-CA", "Entrée Réducteur", "Sortie Réducteur",
            "P-CA", "P-COA", "A1-CA", "A1-COA", "A2-CA", "A2-COA",
            "A3-CA", "A3-COA", "A4-CA", "A4-COA", "A5-CA", "A5-COA"
        ]

        dept_suivi = st.selectbox(
            "1️⃣ Département",
            options=sorted(df_equipements['departement'].unique()),
            key="dept_select_suivi"
        )

        equipements_dept_suivi = df_equipements[
            df_equipements["departement"] == dept_suivi
        ]

        with st.form("form_suivi", clear_on_submit=True):

            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                id_suivi = st.selectbox(
                    "2️⃣ Équipement",
                    options=sorted(equipements_dept_suivi["id_equipement"].tolist()),
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
                    min_value=datetime(1990, 1, 1).date(),
                    max_value=datetime(2099, 1, 1).date(),
                    key="form_suivi_date"
                )

            st.markdown("##")

            col_v, col_twf, col_crest, col_peak = st.columns(4)

            with col_v:
                vitesse_rpm = st.number_input(
                    "Vitesse (RPM) *",
                    min_value=0.0, max_value=10000.0,
                    value=0.0, step=10.0, format="%.2f",
                    key="form_suivi_vitesse"
                )

            with col_twf:
                twf_rms_g = st.number_input(
                    "TWF RMS (g) *",
                    min_value=0.0, max_value=100.0,
                    value=0.0, step=0.01, format="%.3f",
                    key="form_suivi_twf_rms"
                )

            with col_crest:
                crest_factor = st.number_input(
                    "CREST FACTOR *",
                    min_value=0.0, max_value=100.0,
                    value=0.0, step=0.1, format="%.3f",
                    key="form_suivi_crest"
                )

            with col_peak:
                twf_peak = st.number_input(
                    "TWF Peak to Peak (g) *",
                    min_value=0.0, max_value=100.0,
                    value=0.0, step=0.01, format="%.3f",
                    key="form_suivi_peak"
                )

            st.markdown("##")

            col_info, col_btn_suivi = st.columns([3, 1])

            with col_info:
                st.caption("📌 Tous les champs sont requis pour la saisie")

            with col_btn_suivi:
                submitted_suivi = st.form_submit_button(
                    "✅ Enregistrer mesure",
                    type="primary",
                    use_container_width=True
                )

            if submitted_suivi:
                if (vitesse_rpm == 0.0 and twf_rms_g == 0.0
                        and crest_factor == 0.0 and twf_peak == 0.0):
                    st.error("⚠️ Au moins une mesure doit être différente de zéro")
                else:
                    success, message = sauvegarder_suivi(
                        id_suivi, point_mesure, date_suivi,
                        vitesse_rpm, twf_rms_g, crest_factor, twf_peak
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

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

        # Construire un mapping id_equipement → département depuis df_equipements
        equip_to_dept = df_equipements.set_index('id_equipement')['departement'].to_dict()

        # ── ÉQUIPEMENT PRINCIPAL ──────────────────────────────────────────────
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            # Départements qui ont des données de suivi
            depts_avec_suivi = sorted(
                df_suivi['id_equipement']
                .map(equip_to_dept)
                .dropna()
                .unique()
            )
            dept_tendances = st.selectbox(
                "1️⃣ Département",
                options=depts_avec_suivi,
                key="dept_tendances"
            )

        # Équipements du département sélectionné qui ont des données de suivi
        equips_dept_tendances = sorted([
            eq for eq in df_suivi['id_equipement'].unique()
            if equip_to_dept.get(eq) == dept_tendances
        ])

        with col_f2:
            id_equip_suivi = st.selectbox(
                "2️⃣ Équipement",
                options=equips_dept_tendances,
                key="id_equip_tendances"
            )

        with col_f3:
            df_equip_suivi = df_suivi[df_suivi['id_equipement'] == id_equip_suivi]
            point_mesure_suivi = st.selectbox(
                "3️⃣ Point de mesure",
                options=sorted(df_equip_suivi['point_mesure'].unique()),
                key="point_mesure_tendances"
            )

        # Filtrer les données principales
        df_filtered_suivi = df_suivi[
            (df_suivi['id_equipement'] == id_equip_suivi) &
            (df_suivi['point_mesure'] == point_mesure_suivi)
        ].copy()

        if df_filtered_suivi.empty:
            st.warning("⚠️ Aucune donnée pour cette sélection")
            return

        df_filtered_suivi = df_filtered_suivi.sort_values('date')

        # ── ÉQUIPEMENT DE COMPARAISON (optionnel) ────────────────────────────
        #st.markdown("##")
        ajouter_comparaison = st.toggle(
            "➕ Ajouter un équipement de comparaison",
            value=False,
            key="toggle_comparaison"
        )

        df_filtered_suivi2 = None
        id_equip_suivi2 = None
        point_mesure_suivi2 = None

        if ajouter_comparaison:
            col_c1, col_c2, col_c3 = st.columns(3)

            with col_c1:
                depts_avec_suivi2 = sorted(
                    df_suivi['id_equipement']
                    .map(equip_to_dept)
                    .dropna()
                    .unique()
                )
                dept_tendances2 = st.selectbox(
                    "1️⃣ Département (comparaison)",
                    options=depts_avec_suivi2,
                    key="dept_tendances2"
                )

            equips_dept_tendances2 = sorted([
                eq for eq in df_suivi['id_equipement'].unique()
                if equip_to_dept.get(eq) == dept_tendances2
            ])

            with col_c2:
                id_equip_suivi2 = st.selectbox(
                    "2️⃣ Équipement (comparaison)",
                    options=equips_dept_tendances2,
                    key="id_equip_tendances2"
                )

            with col_c3:
                df_equip_suivi2 = df_suivi[df_suivi['id_equipement'] == id_equip_suivi2]
                point_mesure_suivi2 = st.selectbox(
                    "3️⃣ Point de mesure (comparaison)",
                    options=sorted(df_equip_suivi2['point_mesure'].unique()),
                    key="point_mesure_tendances2"
                )

            df_filtered_suivi2 = df_suivi[
                (df_suivi['id_equipement'] == id_equip_suivi2) &
                (df_suivi['point_mesure'] == point_mesure_suivi2)
            ].copy().sort_values('date')

            if df_filtered_suivi2.empty:
                st.warning("⚠️ Aucune donnée pour l'équipement de comparaison")
                df_filtered_suivi2 = None

        #st.markdown("##")

        # ── FILTRES TEMPORELS ─────────────────────────────────────────────────
        col_t1, col_t2, col_t3 = st.columns([2, 2, 1])

        with col_t1:
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
                    min_value=datetime(1990, 1, 1).date(),
                    max_value=datetime(2099, 12, 31).date(),
                    key="date_fin_tendances"
                )

            df_filtered_suivi = df_filtered_suivi[
                (df_filtered_suivi['date'].dt.date >= date_debut_suivi) &
                (df_filtered_suivi['date'].dt.date <= date_fin_suivi)
            ]
            if df_filtered_suivi2 is not None:
                df_filtered_suivi2 = df_filtered_suivi2[
                    (df_filtered_suivi2['date'].dt.date >= date_debut_suivi) &
                    (df_filtered_suivi2['date'].dt.date <= date_fin_suivi)
                ]
        else:
            df_filtered_suivi = df_filtered_suivi.tail(22)
            if df_filtered_suivi2 is not None:
                df_filtered_suivi2 = df_filtered_suivi2.tail(22)

        #st.markdown("##")

        # ── SÉLECTION DES VARIABLES ───────────────────────────────────────────
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

        #st.markdown("##")

        # ── CRÉATION DU GRAPHIQUE ─────────────────────────────────────────────
        fig = go.Figure()

        # Palette équipement principal (couleurs originales)
        couleurs_principal = {
            'vitesse_rpm':        '#1f77b4',
            'twf_rms_g':          '#ff7f0e',
            'crest_factor':       '#2ca02c',
            'twf_peak_to_peak_g': '#d62728'
        }

        # Palette équipement de comparaison (nuances distinctes)
        couleurs_comparaison = {
            'vitesse_rpm':        '#aec7e8',
            'twf_rms_g':          '#c5b0d5',
            'crest_factor':       '#98df8a',
            'twf_peak_to_peak_g': '#ff9896'
        }

        # Traces équipement principal
        for var in variables_selectionnees:
            df_trace = (
                df_filtered_suivi[['date', var]]
                .dropna(subset=['date', var])
                .drop_duplicates(subset='date')
                .sort_values('date')
            )
            legend_label = (
                f"{variables_disponibles[var]} — {id_equip_suivi} | {point_mesure_suivi}"
                if df_filtered_suivi2 is not None
                else variables_disponibles[var]
            )
            fig.add_trace(go.Scatter(
                x=df_trace['date'],
                y=df_trace[var],
                mode='lines+markers',
                name=legend_label,
                connectgaps=True,
                line=dict(color=couleurs_principal[var], width=2),
                marker=dict(size=6, symbol='circle')
            ))

        # Traces équipement de comparaison
        if df_filtered_suivi2 is not None and not df_filtered_suivi2.empty:
            for var in variables_selectionnees:
                df_trace2 = (
                    df_filtered_suivi2[['date', var]]
                    .dropna(subset=['date', var])
                    .drop_duplicates(subset='date')
                    .sort_values('date')
                )
                fig.add_trace(go.Scatter(
                    x=df_trace2['date'],
                    y=df_trace2[var],
                    mode='lines+markers',
                    name=f"{variables_disponibles[var]} — {id_equip_suivi2} | {point_mesure_suivi2}",
                    connectgaps=True,
                    line=dict(color=couleurs_comparaison[var], width=2), #, dash='dash'),
                    marker=dict(size=6, symbol='circle')#symbol='diamond')
                ))

        # Titre dynamique
        if df_filtered_suivi2 is not None:
            titre = (
                f"Tendances — {id_equip_suivi} ({point_mesure_suivi})"
                f"  vs  {id_equip_suivi2} ({point_mesure_suivi2})"
            )
        else:
            titre = f"Tendances - {id_equip_suivi} - {point_mesure_suivi}"

        # Mise en forme (identique à l'original)
        fig.update_layout(
            title=titre,
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

        # ── Statistiques ──────────────────────────────────────────────────────
        st.markdown("##")
        st.caption(f"**{len(df_filtered_suivi)}** mesure(s) affichée(s) — {id_equip_suivi} | {point_mesure_suivi}")
        if df_filtered_suivi2 is not None and not df_filtered_suivi2.empty:
            st.caption(f"**{len(df_filtered_suivi2)}** mesure(s) affichée(s) — {id_equip_suivi2} | {point_mesure_suivi2}")

        with st.expander("📊 Statistiques détaillées"):
            if df_filtered_suivi2 is not None:
                st.markdown(f"**{id_equip_suivi} — {point_mesure_suivi}**")
            stats_data = []
            for var in variables_selectionnees:
                stats_data.append({
                    'Variable': variables_disponibles[var],
                    'Minimum': f"{df_filtered_suivi[var].min():.3f}",
                    'Maximum': f"{df_filtered_suivi[var].max():.3f}",
                    'Moyenne': f"{df_filtered_suivi[var].mean():.3f}",
                    'Variance': f"{df_filtered_suivi[var].var():.3f}",
                    'Écart-type': f"{df_filtered_suivi[var].std():.3f}"
                })
            st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

            if df_filtered_suivi2 is not None and not df_filtered_suivi2.empty:
                st.markdown("---")
                st.markdown(f"**{id_equip_suivi2} — {point_mesure_suivi2}**")
                stats_data2 = []
                for var in variables_selectionnees:
                    stats_data2.append({
                        'Variable': variables_disponibles[var],
                        'Minimum': f"{df_filtered_suivi2[var].min():.3f}",
                        'Maximum': f"{df_filtered_suivi2[var].max():.3f}",
                        'Moyenne': f"{df_filtered_suivi2[var].mean():.3f}",
                        'Variance': f"{df_filtered_suivi[var].var():.3f}",
                        'Écart-type': f"{df_filtered_suivi2[var].std():.3f}"
                    })
                st.dataframe(pd.DataFrame(stats_data2), use_container_width=True, hide_index=True)