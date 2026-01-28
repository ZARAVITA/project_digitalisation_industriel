"""
Onglet Téléchargements - Export Excel filtré
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data.data_manager import (
    charger_equipements,
    charger_observations,
    charger_suivi,
    exporter_observations_excel,
    exporter_equipements_excel,
    exporter_suivi_excel
)


def render():
    """Affiche l'onglet Téléchargements"""

    st.header("📥 Exports Excel")
    st.caption("Générez des fichiers Excel propres et exploitables")

    # Chargement données
    df_equipements = charger_equipements()
    df_observations = charger_observations()
    df_suivi = charger_suivi()

    if df_equipements.empty:
        st.warning("⚠️ Aucun équipement disponible")
        return

    # =============================================================================
    # CARTE 1 : RAPPORT D'OBSERVATIONS
    # =============================================================================

    with st.container(border=True):
        st.subheader("📊 Rapport d'observations")

        if df_observations.empty:
            st.info("ℹ️ Aucune observation à exporter")
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
                # Équipements disponibles
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
                    st.caption(f"🏢 Départements : {', '.join(dept_filter)}")
                if equip_filter:
                    st.caption(f"🔧 Équipements : {', '.join(equip_filter)}")

                st.caption(f"📅 Période : {date_debut} → {date_fin}")

            with col_btn:
                if len(df_filtered) > 0:
                    fichier = exporter_observations_excel(df_filtered, df_equipements)

                    # Nom fichier intelligent
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                    nom_fichier = f"rapport_observations_{timestamp}.xlsx"

                    st.download_button(
                        label="📥 Télécharger",
                        data=fichier,
                        file_name=nom_fichier,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary"
                    )
                else:
                    st.button(
                        "📥 Télécharger",
                        disabled=True,
                        use_container_width=True
                    )
                    st.caption("Aucune donnée")

    # =============================================================================
    # CARTE 2 : ÉQUIPEMENTS
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📦 Liste des équipements")

        # Filtre département
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
                st.caption(f"🏢 Départements : {', '.join(dept_filter_equip)}")
            else:
                st.caption("🏢 Tous les départements")

        with col_btn2:
            if len(df_filtered_equip) > 0:
                fichier_equip = exporter_equipements_excel(df_filtered_equip)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                nom_fichier_equip = f"equipements_{timestamp}.xlsx"

                st.download_button(
                    label="📥 Télécharger",
                    data=fichier_equip,
                    file_name=nom_fichier_equip,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.button(
                    "📥 Télécharger",
                    disabled=True,
                    use_container_width=True
                )

    # =============================================================================
    # CARTE 3 : RAPPORT DE SUIVI DE MESURES (NOUVEAU)
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📈 Rapport de suivi de mesures")
        st.caption("Export professionnel avec tableaux et graphiques intégrés")

        if df_suivi.empty:
            st.info("ℹ️ Aucune donnée de suivi à exporter")
        else:
            # Conversion dates
            df_suivi_export = df_suivi.copy()
            df_suivi_export['date'] = pd.to_datetime(df_suivi_export['date'], errors='coerce')

            # Filtres
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                # Filtre ID équipement
                equip_suivi_filter = st.multiselect(
                    "ID Équipement(s)",
                    options=sorted(df_suivi_export['id_equipement'].unique()),
                    default=None,
                    placeholder="Tous les équipements",
                    key="dl_suivi_equip"
                )

            with col_f2:
                # Filtre point de mesure
                if equip_suivi_filter:
                    points_disponibles = df_suivi_export[
                        df_suivi_export['id_equipement'].isin(equip_suivi_filter)
                    ]['point_mesure'].unique()
                else:
                    points_disponibles = df_suivi_export['point_mesure'].unique()

                points_suivi_filter = st.multiselect(
                    "Point(s) de mesure",
                    options=sorted(points_disponibles),
                    default=None,
                    placeholder="Tous les points",
                    key="dl_suivi_points"
                )

            # Intervalle dates
            col_d1, col_d2 = st.columns(2)

            date_min_suivi = df_suivi_export['date'].min().date()
            date_max_suivi = df_suivi_export['date'].max().date()

            with col_d1:
                date_debut_suivi = st.date_input(
                    "Date début",
                    value=date_min_suivi,
                    min_value=date_min_suivi,
                    max_value=date_max_suivi,
                    key="dl_suivi_date_start"
                )

            with col_d2:
                date_fin_suivi = st.date_input(
                    "Date fin",
                    value=date_max_suivi,
                    min_value=date_min_suivi,
                    max_value=date_max_suivi,
                    key="dl_suivi_date_end"
                )

            st.markdown("##")

            # Application filtres
            df_filtered_suivi = df_suivi_export.copy()

            if equip_suivi_filter:
                df_filtered_suivi = df_filtered_suivi[
                    df_filtered_suivi['id_equipement'].isin(equip_suivi_filter)
                ]

            if points_suivi_filter:
                df_filtered_suivi = df_filtered_suivi[
                    df_filtered_suivi['point_mesure'].isin(points_suivi_filter)
                ]

            df_filtered_suivi = df_filtered_suivi[
                (df_filtered_suivi['date'].dt.date >= date_debut_suivi) &
                (df_filtered_suivi['date'].dt.date <= date_fin_suivi)
            ]

            # Bouton export
            col_info3, col_btn3 = st.columns([3, 1])

            with col_info3:
                nb_equipements = df_filtered_suivi['id_equipement'].nunique()
                nb_mesures = len(df_filtered_suivi)

                st.write(f"**{nb_equipements}** équipement(s) | **{nb_mesures}** mesure(s)")

                if equip_suivi_filter:
                    st.caption(f"🔧 Équipements : {', '.join(equip_suivi_filter)}")
                if points_suivi_filter:
                    st.caption(f"📍 Points : {', '.join(points_suivi_filter)}")

                st.caption(f"📅 Période : {date_debut_suivi} → {date_fin_suivi}")

            with col_btn3:
                if len(df_filtered_suivi) > 0:
                    fichier_suivi = exporter_suivi_excel(df_filtered_suivi, df_equipements)

                    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                    nom_fichier_suivi = f"rapport_suivi_mesures_{timestamp}.xlsx"

                    st.download_button(
                        label="📥 Télécharger",
                        data=fichier_suivi,
                        file_name=nom_fichier_suivi,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary"
                    )
                else:
                    st.button(
                        "📥 Télécharger",
                        disabled=True,
                        use_container_width=True
                    )
                    st.caption("Aucune donnée")

            # Informations sur le format
            with st.expander("ℹ️ Format du rapport"):
                st.markdown("""
                **Structure du fichier Excel :**
                
                - **Un onglet par ID équipement**
                - **Tableaux de données** organisés par point de mesure
                - **Graphiques de tendances** intégrés avec toutes les variables :
                  - Vitesse (RPM)
                  - TWF RMS (g)
                  - Crest Factor
                  - TWF Peak-to-Peak (g)
                
                **Avantages :**
                - Données structurées et prêtes à l'emploi
                - Visualisations automatiques
                - Format professionnel pour présentations
                - Facilité d'analyse et de partage
                """)

    # =============================================================================
    # INFORMATIONS COMPLÉMENTAIRES
    # =============================================================================

    st.markdown("##")

    with st.expander("ℹ️ À propos des exports"):
        st.markdown("""
        **Format des fichiers :**
        - Format : Excel (.xlsx)
        - Encodage : UTF-8
        - Colonnes auto-ajustées

        **Observations :**
        - Triées par date décroissante
        - Incluent le département et l'ID équipement
        - Tous les champs sont présents

        **Équipements :**
        - Triés par département puis ID
        - Format simple : ID + Département
        
        **Suivi de mesures :**
        - Organisation par équipement (un onglet par équipement)
        - Données complètes avec toutes les variables
        - Graphiques intégrés pour visualisation directe
        """)