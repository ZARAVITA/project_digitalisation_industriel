"""
Onglet Équipements - Visualisation et gestion du référentiel
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data.data_manager import (
    charger_equipements,
    exporter_equipements_excel
)


def render():
    """Affiche l'onglet Équipements"""

    st.header("📦 Référentiel des Équipements")
    st.caption("Visualisation et export des équipements par département")

    # Chargement données
    df_equipements = charger_equipements()

    if df_equipements.empty:
        st.warning("⚠️ Aucun équipement trouvé dans le système")
        return

    # =============================================================================
    # BLOC 1 : TABLEAU ET FILTRES
    # =============================================================================

    with st.container(border=True):
        st.subheader("📋 Liste des équipements")

        # Filtre département
        col_filter, col_stats = st.columns([3, 1])

        with col_filter:
            departements = sorted(df_equipements['departement'].unique())
            dept_selectionnes = st.multiselect(
                "Filtrer par département",
                options=departements,
                default=None,
                placeholder="Tous les départements"
            )

        # Application filtre
        if dept_selectionnes:
            df_filtered = df_equipements[
                df_equipements['departement'].isin(dept_selectionnes)
            ]
        else:
            df_filtered = df_equipements.copy()

        with col_stats:
            st.metric(
                "Total équipements",
                len(df_filtered),
                delta=None
            )

        # Tableau
        df_display = df_filtered.sort_values(['departement', 'id_equipement'])

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                'id_equipement': st.column_config.TextColumn(
                    'ID Équipement',
                    width='medium'
                ),
                'departement': st.column_config.TextColumn(
                    'Département',
                    width='medium'
                )
            }
        )

    # =============================================================================
    # BLOC 2 : EXPORT
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📥 Export Excel")

        col_desc, col_btn = st.columns([3, 1])

        with col_desc:
            if dept_selectionnes:
                st.write(f"**{len(df_filtered)}** équipement(s) sélectionné(s)")
                st.caption(f"Départements : {', '.join(dept_selectionnes)}")
            else:
                st.write(f"**{len(df_filtered)}** équipement(s) - Tous départements")

        with col_btn:
            if len(df_filtered) > 0:
                fichier_excel = exporter_equipements_excel(df_filtered)

                # Nom fichier intelligent
                if dept_selectionnes and len(dept_selectionnes) == 1:
                    nom_dept = dept_selectionnes[0].replace(' ', '_')
                    nom_fichier = f"equipements_{nom_dept}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                else:
                    nom_fichier = f"equipements_{datetime.now().strftime('%Y%m%d')}.xlsx"

                st.download_button(
                    label="📥 Télécharger",
                    data=fichier_excel,
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

    # =============================================================================
    # BLOC 3 : STATISTIQUES
    # =============================================================================

    st.markdown("##")

    with st.container(border=True):
        st.subheader("📊 Statistiques par département")

        stats = df_equipements.groupby('departement').size().reset_index(name='Nombre')
        stats = stats.sort_values('Nombre', ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.dataframe(
                stats,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'departement': 'Département',
                    'Nombre': st.column_config.NumberColumn(
                        'Nombre d\'équipements',
                        format='%d'
                    )
                }
            )

        with col2:
            st.metric("Total départements", len(stats))
            st.metric("Total équipements", stats['Nombre'].sum())