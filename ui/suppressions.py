"""
Onglet Suppressions - Zone critique pour corrections
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data.data_manager import (
    charger_equipements,
    charger_observations,
    charger_suivi,
    supprimer_observation,
    supprimer_equipement,
    supprimer_suivi
)


def render():
    """Affiche l'onglet Suppressions"""

    st.header("🗑️ Suppressions")
    st.caption("⚠️ Zone critique - Utilisez avec précaution")

    # Chargement données
    df_equipements = charger_equipements()
    df_observations = charger_observations()
    df_suivi = charger_suivi()

    if df_equipements.empty:
        st.warning("⚠️ Aucun équipement disponible")
        return

    # =============================================================================
    # CARTE 1 : SUPPRESSION D'OBSERVATIONS
    # =============================================================================
    with st.container(border=True):
        st.subheader("🔴 Supprimer une observation")
        st.caption("Suppression ciblée par département, équipement et date")

        if df_observations.empty:
            st.info("ℹ️ Aucune observation à supprimer")
        else:
            # Sélection département HORS formulaire pour réactivité
            departements = sorted(df_equipements['departement'].unique())
            dept_obs_select = st.selectbox(
                "1️⃣ Sélectionner le département",
                options=departements,
                key="dept_obs_suppr"
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
                # Sélection équipement HORS formulaire
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    id_obs_suppr = st.selectbox(
                        "2️⃣ Équipement",
                        options=sorted(equipements_avec_obs['id_equipement'].tolist()),
                        key="suppr_obs_equip"
                    )

                with col2:
                    # Filtrer les dates disponibles pour cet équipement
                    obs_equip = df_observations[
                        df_observations['id_equipement'] == id_obs_suppr
                    ].copy()

                    obs_equip['date'] = pd.to_datetime(obs_equip['date'])
                    dates_disponibles = sorted(
                        obs_equip['date'].dt.date.unique(),
                        reverse=True
                    )

                    if dates_disponibles:
                        date_obs_suppr = st.selectbox(
                            "3️⃣ Date observation",
                            options=dates_disponibles,
                            key="suppr_obs_date"
                        )
                    else:
                        st.warning("Aucune date disponible")
                        date_obs_suppr = None

                with col3:
                    st.write("")
                    st.write("")

                    # Initialiser l'état de confirmation
                    if 'confirm_obs_delete' not in st.session_state:
                        st.session_state.confirm_obs_delete = False

                    # Premier bouton : Demander confirmation
                    if date_obs_suppr and not st.session_state.confirm_obs_delete:
                        if st.button(
                                "🗑️ Supprimer",
                                type="secondary",
                                use_container_width=True,
                                key="btn_suppr_obs_initial"
                        ):
                            st.session_state.confirm_obs_delete = True
                            st.rerun()

                # Afficher la confirmation si demandée
                if date_obs_suppr and st.session_state.confirm_obs_delete:
                    st.markdown("---")
                    st.warning(
                        f"⚠️ **Confirmer la suppression ?**\n\n"
                        f"Département : **{dept_obs_select}**\n\n"
                        f"Équipement : **{id_obs_suppr}**\n\n"
                        f"Date : **{date_obs_suppr}**"
                    )

                    col_confirm, col_cancel = st.columns(2)

                    with col_confirm:
                        if st.button(
                                "✅ Confirmer",
                                type="primary",
                                use_container_width=True,
                                key="btn_confirm_obs"
                        ):
                            success, message = supprimer_observation(
                                id_obs_suppr,
                                date_obs_suppr
                            )

                            if success:
                                st.success(message)
                                st.session_state.confirm_obs_delete = False
                                st.rerun()
                            else:
                                st.error(message)
                                st.session_state.confirm_obs_delete = False

                    with col_cancel:
                        if st.button(
                                "❌ Annuler",
                                use_container_width=True,
                                key="btn_cancel_obs"
                        ):
                            st.session_state.confirm_obs_delete = False
                            st.rerun()

    # =============================================================================
    # CARTE 2 : SUPPRESSION DE SUIVI DE MESURE (NOUVEAU)
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("🔴 Supprimer un suivi de mesure")
        st.caption("Suppression ciblée par département, équipement, point de mesure et date")

        if df_suivi.empty:
            st.info("ℹ️ Aucun suivi à supprimer")
        else:
            # Sélection département HORS formulaire
            departements_suivi = sorted(df_equipements['departement'].unique())
            dept_suivi_select = st.selectbox(
                "1️⃣ Sélectionner le département",
                options=departements_suivi,
                key="dept_suivi_suppr"
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
                # Sélection équipement
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                with col1:
                    id_suivi_suppr = st.selectbox(
                        "2️⃣ Équipement",
                        options=sorted(equipements_avec_suivi['id_equipement'].tolist()),
                        key="suppr_suivi_equip"
                    )

                with col2:
                    # Filtrer les points de mesure disponibles pour cet équipement
                    suivi_equip = df_suivi[
                        df_suivi['id_equipement'] == id_suivi_suppr
                    ].copy()

                    points_disponibles = sorted(suivi_equip['point_mesure'].unique())

                    if points_disponibles:
                        point_suivi_suppr = st.selectbox(
                            "3️⃣ Point de mesure",
                            options=points_disponibles,
                            key="suppr_suivi_point"
                        )
                    else:
                        st.warning("Aucun point disponible")
                        point_suivi_suppr = None

                with col3:
                    if point_suivi_suppr:
                        # Filtrer les dates disponibles
                        suivi_point = suivi_equip[
                            suivi_equip['point_mesure'] == point_suivi_suppr
                        ].copy()

                        suivi_point['date'] = pd.to_datetime(suivi_point['date'])
                        dates_suivi_disponibles = sorted(
                            suivi_point['date'].dt.date.unique(),
                            reverse=True
                        )

                        if dates_suivi_disponibles:
                            date_suivi_suppr = st.selectbox(
                                "4️⃣ Date",
                                options=dates_suivi_disponibles,
                                key="suppr_suivi_date"
                            )
                        else:
                            st.warning("Aucune date disponible")
                            date_suivi_suppr = None
                    else:
                        date_suivi_suppr = None

                with col4:
                    st.write("")
                    st.write("")

                    # Initialiser l'état de confirmation
                    if 'confirm_suivi_delete' not in st.session_state:
                        st.session_state.confirm_suivi_delete = False

                    # Premier bouton : Demander confirmation
                    if date_suivi_suppr and point_suivi_suppr and not st.session_state.confirm_suivi_delete:
                        if st.button(
                                "🗑️ Supprimer",
                                type="secondary",
                                use_container_width=True,
                                key="btn_suppr_suivi_initial"
                        ):
                            st.session_state.confirm_suivi_delete = True
                            st.rerun()

                # Afficher la confirmation si demandée
                if (date_suivi_suppr and point_suivi_suppr and
                    st.session_state.confirm_suivi_delete):

                    # Récupérer les valeurs pour affichage
                    ligne_suivi = suivi_point[
                        suivi_point['date'].dt.date == date_suivi_suppr
                    ].iloc[0]

                    st.markdown("---")
                    st.warning(
                        f"⚠️ **Confirmer la suppression du suivi ?**\n\n"
                        f"**Département :** {dept_suivi_select}\n\n"
                        f"**Équipement :** {id_suivi_suppr}\n\n"
                        f"**Point de mesure :** {point_suivi_suppr}\n\n"
                        f"**Date :** {date_suivi_suppr}\n\n"
                        f"**Valeurs :**\n"
                        f"- Vitesse: {ligne_suivi['vitesse_rpm']:.2f} RPM\n"
                        f"- TWF RMS: {ligne_suivi['twf_rms_g']:.2f} g\n"
                        f"- Crest Factor: {ligne_suivi['crest_factor']:.2f}\n"
                        f"- TWF Peak-to-Peak: {ligne_suivi['twf_peak_to_peak_g']:.2f} g"
                    )

                    col_confirm, col_cancel = st.columns(2)

                    with col_confirm:
                        if st.button(
                                "✅ Confirmer",
                                type="primary",
                                use_container_width=True,
                                key="btn_confirm_suivi"
                        ):
                            success, message = supprimer_suivi(
                                id_suivi_suppr,
                                point_suivi_suppr,
                                date_suivi_suppr
                            )

                            if success:
                                st.success(message)
                                st.session_state.confirm_suivi_delete = False
                                st.rerun()
                            else:
                                st.error(message)
                                st.session_state.confirm_suivi_delete = False

                    with col_cancel:
                        if st.button(
                                "❌ Annuler",
                                use_container_width=True,
                                key="btn_cancel_suivi"
                        ):
                            st.session_state.confirm_suivi_delete = False
                            st.rerun()

    # =============================================================================
    # CARTE 3 : SUPPRESSION D'ÉQUIPEMENTS
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("🔴 Supprimer un équipement")
        st.caption("⚠️ Suppression de l'équipement ET de toutes ses observations")

        # Sélection département HORS formulaire pour réactivité
        departements_equip = sorted(df_equipements['departement'].unique())
        dept_equip_select = st.selectbox(
            "1️⃣ Sélectionner le département",
            options=departements_equip,
            key="dept_equip_suppr"
        )

        # Filtrer équipements par département
        equipements_dept_equip = df_equipements[
            df_equipements['departement'] == dept_equip_select
        ]

        if equipements_dept_equip.empty:
            st.warning(f"⚠️ Aucun équipement dans le département '{dept_equip_select}'")
        else:
            col1, col2 = st.columns([3, 1])

            with col1:
                id_equip_suppr = st.selectbox(
                    "2️⃣ Sélectionner l'équipement à supprimer",
                    options=sorted(equipements_dept_equip['id_equipement'].tolist()),
                    key="suppr_equip_id"
                )

                # Nombre d'observations et de suivis
                nb_obs = len(
                    df_observations[df_observations['id_equipement'] == id_equip_suppr]
                )
                nb_suivi = len(
                    df_suivi[df_suivi['id_equipement'] == id_equip_suppr]
                )

                st.caption(f"🏢 Département : **{dept_equip_select}**")
                st.caption(f"📊 **{nb_obs}** observation(s) associée(s)")
                st.caption(f"📈 **{nb_suivi}** suivi(s) associé(s)")

            with col2:
                st.write("")  # Espacement
                st.write("")

                # Initialiser l'état de confirmation
                if 'confirm_equip_delete' not in st.session_state:
                    st.session_state.confirm_equip_delete = False

                # Premier clic : demander confirmation
                if not st.session_state.confirm_equip_delete:
                    if st.button(
                            "🗑️ Supprimer",
                            type="secondary",
                            use_container_width=True,
                            key="btn_suppr_equip_initial"
                    ):
                        st.session_state.confirm_equip_delete = True
                        st.rerun()

            # Afficher la confirmation si demandée
            if st.session_state.confirm_equip_delete:
                st.markdown("---")
                st.error(
                    f"🚨 **ATTENTION - SUPPRESSION DÉFINITIVE**\n\n"
                    f"Département : **{dept_equip_select}**\n\n"
                    f"Équipement : **{id_equip_suppr}**\n\n"
                    f"⚠️ Cette action supprimera également :\n"
                    f"- **{nb_obs} observation(s)** associée(s)\n"
                    f"- **{nb_suivi} suivi(s)** associé(s)\n\n"
                    f"**Cette action est irréversible !**"
                )

                col_confirm, col_cancel = st.columns(2)

                with col_confirm:
                    if st.button(
                            "✅ Confirmer suppression",
                            type="primary",
                            use_container_width=True,
                            key="btn_confirm_equip"
                    ):
                        success, message = supprimer_equipement(id_equip_suppr)

                        if success:
                            st.success(message)
                            st.session_state.confirm_equip_delete = False
                            st.rerun()
                        else:
                            st.error(message)
                            st.session_state.confirm_equip_delete = False

                with col_cancel:
                    if st.button(
                            "❌ Annuler",
                            use_container_width=True,
                            key="btn_cancel_equip"
                    ):
                        st.session_state.confirm_equip_delete = False
                        st.rerun()

    # =============================================================================
    # INFORMATIONS DE SÉCURITÉ
    # =============================================================================

    st.markdown("##")

    with st.expander("ℹ️ Consignes de sécurité"):
        st.markdown("""
        **⚠️ Règles importantes :**

        1. **Suppression d'observations :**
           - Sélectionnez d'abord le département
           - Puis l'équipement concerné
           - Enfin la date exacte de l'observation
           - Aucun impact sur l'équipement lui-même

        2. **Suppression de suivi de mesure :**
           - Sélectionnez d'abord le département
           - Puis l'équipement concerné
           - Ensuite le point de mesure
           - Enfin la date exacte du suivi
           - Supprime uniquement l'enregistrement ciblé

        3. **Suppression d'équipements :**
           - Sélectionnez d'abord le département
           - Puis l'équipement à supprimer
           - Supprime l'équipement du référentiel
           - Supprime TOUTES les observations associées
           - Supprime TOUS les suivis associés
           - Action irréversible

        4. **Bonnes pratiques :**
           - Vérifiez toujours les informations avant de confirmer
           - Exportez vos données régulièrement
           - En cas de doute, consultez un responsable

        5. **Récupération :**
           - Aucune récupération possible après confirmation
           - Assurez-vous d'avoir des sauvegardes à jour
        """)