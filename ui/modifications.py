"""
Onglet Modifications - Modification des observations et suivis
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data.data_manager import (
    charger_equipements,
    charger_observations,
    charger_suivi,
    modifier_observation,
    modifier_suivi
)


def render():
    """Affiche l'onglet Modifications"""

    st.header("✏️ Modifications")
    st.caption("Modification des observations et des suivis de mesures")

    # Chargement données
    df_equipements = charger_equipements()
    df_observations = charger_observations()
    df_suivi = charger_suivi()

    if df_equipements.empty:
        st.warning("⚠️ Aucun équipement disponible")
        return

    # =============================================================================
    # CARTE 1 : MODIFICATION D'OBSERVATIONS
    # =============================================================================
    with st.container(border=True):
        st.subheader("📝 Modifier une observation")
        st.caption("Modification ciblée par département, équipement et date")

        if df_observations.empty:
            st.info("ℹ️ Aucune observation à modifier")
        else:
            # Sélection département HORS formulaire pour réactivité
            departements = sorted(df_equipements['departement'].unique())
            dept_obs_select = st.selectbox(
                "1️⃣ Sélectionner le département",
                options=departements,
                key="dept_obs_modif"
            )

            # Filtrer équipements par département
            equipements_dept = df_equipements[
                df_equipements['departement'] == dept_obs_select
            ]

            # Filtrer seulement les équipements qui ont des observations
            ids_avec_obs = df_observations['id_equipement'].unique()
            equipements_avec_obs = equipements_dept[
                equipements_dept['id_equipement'].isin(ids_avec_obs)
            ]

            if equipements_avec_obs.empty:
                st.warning(f"⚠️ Aucune observation dans le département '{dept_obs_select}'")
            else:
                # Sélection équipement
                col1, col2 = st.columns([2, 2])

                with col1:
                    id_obs_modif = st.selectbox(
                        "2️⃣ Équipement",
                        options=sorted(equipements_avec_obs['id_equipement'].tolist()),
                        key="modif_obs_equip"
                    )

                with col2:
                    # Filtrer les dates disponibles pour cet équipement
                    obs_equip = df_observations[
                        df_observations['id_equipement'] == id_obs_modif
                    ].copy()

                    obs_equip['date'] = pd.to_datetime(obs_equip['date'])
                    dates_disponibles = sorted(
                        obs_equip['date'].dt.date.unique(),
                        reverse=True
                    )

                    if dates_disponibles:
                        date_obs_modif = st.selectbox(
                            "3️⃣ Date observation",
                            options=dates_disponibles,
                            key="modif_obs_date"
                        )
                    else:
                        st.warning("Aucune date disponible")
                        date_obs_modif = None

                # Afficher le formulaire de modification si une date est sélectionnée
                if date_obs_modif:
                    st.markdown("---")
                    st.subheader("✏️ Modifier les données")

                    # Récupérer les données actuelles
                    obs_actuelle = obs_equip[
                        obs_equip['date'].dt.date == date_obs_modif
                    ].iloc[0]

                    # Formulaire de modification
                    with st.form("form_modif_observation"):
                        st.caption("📌 Modifiez les champs souhaités")

                        # Ligne 1 : Nouvelle date et analyste
                        col_date, col_analyste = st.columns(2)

                        with col_date:
                            nouvelle_date = st.date_input(
                                "Nouvelle date",
                                value=date_obs_modif,
                                min_value=datetime(1990, 1, 1).date(),
                                max_value=datetime(2099, 12, 31).date(),
                                key="form_modif_obs_date"
                            )

                        with col_analyste:
                            nouvel_analyste = st.text_input(
                                "Analyste *",
                                value=obs_actuelle.get('analyste', ''),
                                placeholder="Nom de l'analyste",
                                key="form_modif_obs_analyste"
                            )

                        st.markdown("##")

                        # Ligne 2 : Champs texte
                        col_obs, col_reco, col_trav = st.columns(3)

                        with col_obs:
                            nouvelle_observation = st.text_area(
                                "Observation *",
                                value=obs_actuelle.get('observation', ''),
                                height=120,
                                placeholder="Décrivez l'état constaté, anomalies...",
                                key="form_modif_obs_text"
                            )

                        with col_reco:
                            nouvelle_recommandation = st.text_area(
                                "Recommandation",
                                value=obs_actuelle.get('recommandation', ''),
                                height=120,
                                placeholder="Actions à entreprendre, pièces à commander...",
                                key="form_modif_obs_reco"
                            )

                        with col_trav:
                            nouveaux_travaux = st.text_area(
                                "Travaux effectués & Notes",
                                value=obs_actuelle.get('Travaux effectués & Notes', ''),
                                height=120,
                                placeholder="Travaux réalisés et remarques...",
                                key="form_modif_obs_trav"
                            )

                        st.markdown("##")

                        # Ligne 3 : Importance
                        importance_options = [
                            "",
                            "Très important",
                            "Important",
                            "Moins important",
                            "Pas de collecte mais important",
                            "Collecte réalisée"
                        ]

                        # Récupérer l'importance actuelle (peut être vide)
                        importance_actuelle = obs_actuelle.get('importance', '')
                        if importance_actuelle and importance_actuelle in importance_options:
                            index_importance = importance_options.index(importance_actuelle)
                        else:
                            index_importance = 0

                        nouvelle_importance = st.selectbox(
                            "Importance",
                            options=importance_options,
                            index=index_importance,
                            key="form_modif_obs_importance",
                            help="Sélectionnez le niveau d'importance (optionnel)"
                        )

                        st.markdown("##")

                        # Bouton de soumission
                        col_info, col_btn = st.columns([3, 1])

                        with col_info:
                            st.caption("📌 Les champs requis sont marqués d'un astérisque (*)")

                        with col_btn:
                            submitted = st.form_submit_button(
                                "✅ Enregistrer modifications",
                                type="primary",
                                use_container_width=True
                            )

                        # Validation et enregistrement
                        if submitted:
                            if not nouvelle_observation.strip():
                                st.error("⚠️ L'observation est requise")
                            elif not nouvel_analyste.strip():
                                st.error("⚠️ Le nom de l'analyste est requis")
                            else:
                                # Appeler la fonction de modification
                                success, message = modifier_observation(
                                    id_equipement=id_obs_modif,
                                    date_originale=date_obs_modif,
                                    nouvelle_date=nouvelle_date,
                                    observation=nouvelle_observation.strip(),
                                    recommandation=nouvelle_recommandation.strip(),
                                    travaux_notes=nouveaux_travaux.strip(),
                                    analyste=nouvel_analyste.strip(),
                                    importance=nouvelle_importance if nouvelle_importance else None
                                )

                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)

    # =============================================================================
    # CARTE 2 : MODIFICATION DE SUIVI DE MESURE
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📈 Modifier un suivi de mesure")
        st.caption("Modification ciblée par département, équipement, point de mesure et date")

        if df_suivi.empty:
            st.info("ℹ️ Aucun suivi à modifier")
        else:
            # Sélection département HORS formulaire
            departements_suivi = sorted(df_equipements['departement'].unique())
            dept_suivi_select = st.selectbox(
                "1️⃣ Sélectionner le département",
                options=departements_suivi,
                key="dept_suivi_modif"
            )

            # Filtrer équipements par département
            equipements_dept_suivi = df_equipements[
                df_equipements['departement'] == dept_suivi_select
            ]

            # Filtrer seulement les équipements qui ont des suivis
            ids_avec_suivi = df_suivi['id_equipement'].unique()
            equipements_avec_suivi = equipements_dept_suivi[
                equipements_dept_suivi['id_equipement'].isin(ids_avec_suivi)
            ]

            if equipements_avec_suivi.empty:
                st.warning(f"⚠️ Aucun suivi dans le département '{dept_suivi_select}'")
            else:
                # Sélection équipement et point de mesure
                col1, col2, col3 = st.columns(3)

                with col1:
                    id_suivi_modif = st.selectbox(
                        "2️⃣ Équipement",
                        options=sorted(equipements_avec_suivi['id_equipement'].tolist()),
                        key="modif_suivi_equip"
                    )

                with col2:
                    # Filtrer les points de mesure disponibles pour cet équipement
                    suivi_equip = df_suivi[
                        df_suivi['id_equipement'] == id_suivi_modif
                    ].copy()

                    points_disponibles = sorted(suivi_equip['point_mesure'].unique())

                    if points_disponibles:
                        point_suivi_modif = st.selectbox(
                            "3️⃣ Point de mesure",
                            options=points_disponibles,
                            key="modif_suivi_point"
                        )
                    else:
                        st.warning("Aucun point de mesure disponible")
                        point_suivi_modif = None

                with col3:
                    if point_suivi_modif:
                        # Filtrer les dates pour ce point de mesure
                        suivi_point = suivi_equip[
                            suivi_equip['point_mesure'] == point_suivi_modif
                        ].copy()

                        suivi_point['date'] = pd.to_datetime(suivi_point['date'])
                        dates_suivi_disponibles = sorted(
                            suivi_point['date'].dt.date.unique(),
                            reverse=True
                        )

                        if dates_suivi_disponibles:
                            date_suivi_modif = st.selectbox(
                                "4️⃣ Date mesure",
                                options=dates_suivi_disponibles,
                                key="modif_suivi_date"
                            )
                        else:
                            st.warning("Aucune date disponible")
                            date_suivi_modif = None
                    else:
                        date_suivi_modif = None

                # Afficher le formulaire de modification si tous les paramètres sont sélectionnés
                if point_suivi_modif and date_suivi_modif:
                    st.markdown("---")
                    st.subheader("✏️ Modifier les mesures")

                    # Récupérer les données actuelles
                    suivi_actuel = suivi_point[
                        suivi_point['date'].dt.date == date_suivi_modif
                    ].iloc[0]

                    # Formulaire de modification
                    with st.form("form_modif_suivi"):
                        st.caption("📌 Modifiez les mesures souhaitées")

                        # Afficher les valeurs actuelles
                        with st.expander("📊 Valeurs actuelles", expanded=False):
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.metric("Vitesse (RPM)", f"{suivi_actuel.get('vitesse_rpm', 0):.2f}")
                                st.metric("TWF RMS (g)", f"{suivi_actuel.get('twf_rms_g', 0):.3f}")
                            with col_info2:
                                st.metric("Crest Factor", f"{suivi_actuel.get('crest_factor', 0):.2f}")
                                st.metric("TWF Peak-to-Peak (g)", f"{suivi_actuel.get('twf_peak_to_peak_g', 0):.3f}")

                        st.markdown("##")

                        # Ligne 1 : Nouvelle date
                        nouvelle_date_suivi = st.date_input(
                            "Nouvelle date",
                            value=date_suivi_modif,
                            min_value=datetime(1990, 1, 1).date(),
                            max_value=datetime(2099, 12, 31).date(),
                            key="form_modif_suivi_date"
                        )

                        st.markdown("##")

                        # Ligne 2 : Nouvelles mesures
                        col_vitesse, col_rms = st.columns(2)

                        with col_vitesse:
                            nouvelle_vitesse = st.number_input(
                                "Vitesse (RPM) *",
                                min_value=0.0,
                                max_value=10000.0,
                                value=float(suivi_actuel.get('vitesse_rpm', 0)),
                                step=1.0,
                                format="%.2f",
                                key="form_modif_suivi_vitesse"
                            )

                        with col_rms:
                            nouveau_rms = st.number_input(
                                "TWF RMS (g) *",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(suivi_actuel.get('twf_rms_g', 0)),
                                step=0.001,
                                format="%.3f",
                                key="form_modif_suivi_rms"
                            )

                        # Ligne 3 : Autres mesures
                        col_crest, col_peak = st.columns(2)

                        with col_crest:
                            nouveau_crest = st.number_input(
                                "Crest Factor *",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(suivi_actuel.get('crest_factor', 0)),
                                step=0.01,
                                format="%.2f",
                                key="form_modif_suivi_crest"
                            )

                        with col_peak:
                            nouveau_peak = st.number_input(
                                "TWF Peak to Peak (g) *",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(suivi_actuel.get('twf_peak_to_peak_g', 0)),
                                step=0.001,
                                format="%.3f",
                                key="form_modif_suivi_peak"
                            )

                        st.markdown("##")

                        # Bouton de soumission
                        col_info, col_btn_suivi = st.columns([3, 1])

                        with col_info:
                            st.caption("📌 Tous les champs sont requis")

                        with col_btn_suivi:
                            submitted_suivi = st.form_submit_button(
                                "✅ Enregistrer modifications",
                                type="primary",
                                use_container_width=True
                            )

                        # Validation et enregistrement
                        if submitted_suivi:
                            if (
                                nouvelle_vitesse == 0.0
                                and nouveau_rms == 0.0
                                and nouveau_crest == 0.0
                                and nouveau_peak == 0.0
                            ):
                                st.error("⚠️ Au moins une mesure doit être différente de zéro")
                            else:
                                # Appeler la fonction de modification
                                success, message = modifier_suivi(
                                    id_equipement=id_suivi_modif,
                                    point_mesure_original=point_suivi_modif,
                                    date_originale=date_suivi_modif,
                                    nouvelle_date=nouvelle_date_suivi,
                                    vitesse_rpm=nouvelle_vitesse,
                                    twf_rms_g=nouveau_rms,
                                    crest_factor=nouveau_crest,
                                    twf_peak_to_peak_g=nouveau_peak
                                )

                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)

    # =============================================================================
    # INFORMATIONS COMPLÉMENTAIRES
    # =============================================================================

    st.markdown("##")

    with st.expander("ℹ️ Instructions d'utilisation"):
        st.markdown("""
        **📝 Modification d'observations :**

        1. **Sélection :**
           - Choisissez d'abord le département
           - Puis l'équipement concerné
           - Enfin la date de l'observation à modifier

        2. **Modification :**
           - Tous les champs sont modifiables
           - La date peut être changée
           - Les champs requis sont marqués d'un astérisque (*)
           - L'importance est optionnelle

        3. **Enregistrement :**
           - Cliquez sur "Enregistrer modifications"
           - Les modifications sont appliquées immédiatement
           - L'ancienne observation est remplacée

        ---

        **📈 Modification de suivi de mesure :**

        1. **Sélection :**
           - Choisissez d'abord le département
           - Puis l'équipement concerné
           - Ensuite le point de mesure
           - Enfin la date de la mesure à modifier

        2. **Modification :**
           - Toutes les mesures sont modifiables
           - La date peut être changée
           - Au moins une mesure doit être > 0
           - Les valeurs actuelles sont affichées pour référence

        3. **Enregistrement :**
           - Cliquez sur "Enregistrer modifications"
           - Les modifications sont appliquées immédiatement
           - L'ancien suivi est remplacé

        ---

        **⚠️ Important :**
        - Les modifications sont définitives
        - Vérifiez bien les données avant de valider
        - En cas d'erreur, utilisez à nouveau cette page pour corriger
        """)
