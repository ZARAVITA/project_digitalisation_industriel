"""
Onglet TÃ©lÃ©chargements - Export Excel filtrÃ©
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data.data_manager import (
    charger_equipements,
    charger_observations,
    exporter_observations_excel,
    exporter_equipements_excel
)


def render():
    """Affiche l'onglet TÃ©lÃ©chargements"""

    st.header("Exports Excel")
    st.caption("Générez des fichiers Excel propres et exploitables")

    # Chargement donnÃ©es
    df_equipements = charger_equipements()
    df_observations = charger_observations()

    if df_equipements.empty:
        st.warning("Aucun équipement disponible")
        return

    # =============================================================================
    # CARTE 1 : RAPPORT D'OBSERVATIONS
    # =============================================================================

    with st.container(border=True):
        st.subheader("Rapport d'observations")

        if df_observations.empty:
            st.info("Aucune observation à exporter")
        else:
            # Conversion dates
            df_obs = df_observations.copy()
            df_obs['date'] = pd.to_datetime(df_obs['date'], errors='coerce')

            # Filtres
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                dept_filter = st.multiselect(
                    "Département(s)",
                    options=sorted(df_equipements['departement'].unique()),
                    default=None,
                    placeholder="Tous les départements",
                    key="dl_obs_dept"
                )

            with col_f2:
                # Ã‰quipements disponibles
                if dept_filter:
                    equip_disponibles = df_equipements[
                        df_equipements['departement'].isin(dept_filter)
                    ]['id_equipement'].tolist()
                else:
                    equip_disponibles = df_equipements['id_equipement'].tolist()

                equip_filter = st.multiselect(
                    "Equipement(s)",
                    options=sorted(equip_disponibles),
                    default=None,
                    placeholder="Tous les équipements",
                    key="dl_obs_equip"
                )

            # Intervalle dates
            col_d1, col_d2 = st.columns(2)

            date_min = df_obs['date'].min().date()
            date_max = df_obs['date'].max().date()

            with col_d1:
                date_debut = st.date_input(
                    "Date début",
                    value=date_min,
                    min_value=date_min,
                    max_value=date_max,
                    key="dl_obs_date_start"
                )

            with col_d2:
                date_fin = st.date_input(
                    "Date fin",
                    value=date_max,
                    min_value=date_min,
                    max_value=date_max,
                    key="dl_obs_date_end"
                )

            st.markdown("##")

            # Application filtres
            df_filtered = df_obs.copy()

            if dept_filter:
                ids_dept = df_equipements[
                    df_equipements['departement'].isin(dept_filter)
                ]['id_equipement'].tolist()
                df_filtered = df_filtered[df_filtered['id_equipement'].isin(ids_dept)]

            if equip_filter:
                df_filtered = df_filtered[df_filtered['id_equipement'].isin(equip_filter)]

            df_filtered = df_filtered[
                (df_filtered['date'].dt.date >= date_debut) &
                (df_filtered['date'].dt.date <= date_fin)
                ]

            # Bouton export
            col_info, col_btn = st.columns([3, 1])

            with col_info:
                st.write(f"**{len(df_filtered)}** observation(s) à exporter")

                if dept_filter:
                    st.caption(f"Départements : {', '.join(dept_filter)}")
                if equip_filter:
                    st.caption(f"Equipements : {', '.join(equip_filter)}")

                st.caption(f"Période : {date_debut} à’ {date_fin}")

            with col_btn:
                if len(df_filtered) > 0:
                    fichier = exporter_observations_excel(df_filtered, df_equipements)

                    # Nom fichier intelligent
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                    nom_fichier = f"rapport_observations_{timestamp}.xlsx"

                    st.download_button(
                        label="Télécharger",
                        data=fichier,
                        file_name=nom_fichier,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary"
                    )
                else:
                    st.button(
                        "Télécharger",
                        disabled=True,
                        use_container_width=True
                    )
                    st.caption("Aucune donnée")

    # =============================================================================
    # CARTE 2 : Ã‰QUIPEMENTS
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("Liste des équipements")

        # Filtre dÃ©partement
        dept_filter_equip = st.multiselect(
            "Département(s)",
            options=sorted(df_equipements['departement'].unique()),
            default=None,
            placeholder="Tous les départements",
            key="dl_equip_dept"
        )

        st.markdown("##")

        # Application filtre
        if dept_filter_equip:
            df_filtered_equip = df_equipements[
                df_equipements['departement'].isin(dept_filter_equip)
            ]
        else:
            df_filtered_equip = df_equipements.copy()

        # Bouton export
        col_info2, col_btn2 = st.columns([3, 1])

        with col_info2:
            st.write(f"**{len(df_filtered_equip)}** équipement(s) à exporter")

            if dept_filter_equip:
                st.caption(f" Départements : {', '.join(dept_filter_equip)}")
            else:
                st.caption("Tous les départements")

        with col_btn2:
            if len(df_filtered_equip) > 0:
                fichier_equip = exporter_equipements_excel(df_filtered_equip)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                nom_fichier_equip = f"equipements_{timestamp}.xlsx"

                st.download_button(
                    label="Télécharger",
                    data=fichier_equip,
                    file_name=nom_fichier_equip,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.button(
                    "Télécharger",
                    disabled=True,
                    use_container_width=True
                )

    # =============================================================================
    # INFORMATIONS COMPLÃ‰MENTAIRES
    # =============================================================================

    st.markdown("##")

    with st.expander("À propos des exports"):
        st.markdown("""
        **Format des fichiers :**
        - Format : Excel (.xlsx)
        - Encodage : UTF-8
        - Colonnes auto-ajustées

        **Observations :**
        - Triées par date décroissante
        - Incluent le département et l'ID équipement
        - Tous les champs sont présents

        **Equipements :**
        - Triés par département puis ID
        - Format simple : ID + Département
        """)