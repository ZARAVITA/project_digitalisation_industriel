"""
Onglet Suppressions - Zone critique pour corrections
"""

import streamlit as st
from datetime import datetime
from data.data_manager import (
    charger_equipements,
    charger_observations,
    supprimer_observation,
    supprimer_equipement
)


def render():
    """Affiche l'onglet Suppressions"""

    st.header("🗑️ Suppressions")
    st.caption("⚠️ Zone critique - Utilisez avec précaution")

    # Chargement données
    df_equipements = charger_equipements()
    df_observations = charger_observations()

    if df_equipements.empty:
        st.warning("⚠️ Aucun équipement disponible")
        return

    # =============================================================================
    # CARTE 1 : SUPPRESSION D'OBSERVATIONS
    # =============================================================================

    with st.container(border=True):
        st.subheader("🔴 Supprimer une observation")
        st.caption("Suppression ciblée par équipement et date")

        if df_observations.empty:
            st.info("ℹ️ Aucune observation à supprimer")
        else:
            with st.form("form_suppr_obs"):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    # Liste équipements avec observations
                    equip_avec_obs = df_observations['id_equipement'].unique().tolist()

                    id_obs_suppr = st.selectbox(
                        "Équipement",
                        options=sorted(equip_avec_obs),
                        key="suppr_obs_equip"
                    )

                with col2:
                    date_obs_suppr = st.date_input(
                        "Date observation",
                        value=datetime.now(),
                        key="suppr_obs_date"
                    )

                with col3:
                    st.write("")  # Espacement
                    st.write("")
                    btn_suppr_obs = st.form_submit_button(
                        "🗑️ Supprimer",
                        type="secondary",
                        use_container_width=True
                    )

                # Confirmation
                if btn_suppr_obs:
                    st.markdown("---")
                    st.warning(
                        f"⚠️ **Confirmer la suppression ?**\n\n"
                        f"Équipement : **{id_obs_suppr}**\n\n"
                        f"Date : **{date_obs_suppr}**"
                    )

                    col_confirm, col_cancel = st.columns(2)

                    with col_confirm:
                        if st.form_submit_button(
                                "✅ Confirmer",
                                type="primary",
                                use_container_width=True
                        ):
                            success, message = supprimer_observation(
                                id_obs_suppr,
                                date_obs_suppr
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                    with col_cancel:
                        if st.form_submit_button(
                                "❌ Annuler",
                                use_container_width=True
                        ):
                            st.info("Suppression annulée")

    # =============================================================================
    # CARTE 2 : SUPPRESSION D'ÉQUIPEMENTS
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("🔴 Supprimer un équipement")
        st.caption("⚠️ Suppression de l'équipement ET de toutes ses observations")

        with st.form("form_suppr_equip"):
            col1, col2 = st.columns([3, 1])

            with col1:
                id_equip_suppr = st.selectbox(
                    "Sélectionner l'équipement à supprimer",
                    options=sorted(df_equipements['id_equipement'].tolist()),
                    key="suppr_equip_id"
                )

                # Afficher département et nombre d'observations
                dept = df_equipements[
                    df_equipements['id_equipement'] == id_equip_suppr
                    ]['departement'].values[0]

                nb_obs = len(
                    df_observations[df_observations['id_equipement'] == id_equip_suppr]
                )

                st.caption(f"📍 Département : **{dept}**")
                st.caption(f"📊 **{nb_obs}** observation(s) associée(s)")

            with col2:
                st.write("")  # Espacement
                st.write("")
                btn_suppr_equip = st.form_submit_button(
                    "🗑️ Supprimer",
                    type="secondary",
                    use_container_width=True
                )

            # Confirmation avec avertissement renforcé
            if btn_suppr_equip:
                st.markdown("---")
                st.error(
                    f"🚨 **ATTENTION - SUPPRESSION DÉFINITIVE**\n\n"
                    f"Équipement : **{id_equip_suppr}** ({dept})\n\n"
                    f"⚠️ Cette action supprimera également **{nb_obs} observation(s)** associée(s)\n\n"
                    f"**Cette action est irréversible !**"
                )

                col_confirm2, col_cancel2 = st.columns(2)

                with col_confirm2:
                    if st.form_submit_button(
                            "✅ Confirmer suppression",
                            type="primary",
                            use_container_width=True
                    ):
                        success, message = supprimer_equipement(id_equip_suppr)

                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

                with col_cancel2:
                    if st.form_submit_button(
                            "❌ Annuler",
                            use_container_width=True
                    ):
                        st.info("Suppression annulée")

    # =============================================================================
    # INFORMATIONS DE SÉCURITÉ
    # =============================================================================

    st.markdown("##")

    with st.expander("ℹ️ Consignes de sécurité"):
        st.markdown("""
        **⚠️ Règles importantes :**

        1. **Suppression d'observations :**
           - Supprime une seule observation à la fois
           - Nécessite l'ID équipement ET la date exacte
           - Aucun impact sur l'équipement lui-même

        2. **Suppression d'équipements :**
           - Supprime l'équipement du référentiel
           - Supprime TOUTES les observations associées
           - Action irréversible

        3. **Bonnes pratiques :**
           - Vérifiez toujours les informations avant de confirmer
           - Exportez vos données régulièrement
           - En cas de doute, consultez un responsable

        4. **Récupération :**
           - Aucune récupération possible après confirmation
           - Assurez-vous d'avoir des sauvegardes à jour
        """)