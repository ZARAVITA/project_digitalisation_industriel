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


def sauvegarder_equipement(id_equipement, departement):
    """
    Ajoute un nouvel équipement au référentiel

    Args:
        id_equipement (str): ID de l'équipement
        departement (str): Nom du département

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        df_equip = charger_equipements()

        # Vérifier si l'équipement existe déjà
        if id_equipement in df_equip['id_equipement'].values:
            return False, f"⚠️ L'équipement '{id_equipement}' existe déjà"

        # Ajouter le nouvel équipement
        nouvel_equip = pd.DataFrame([{
            'id_equipement': id_equipement,
            'departement': departement
        }])

        df_equip = pd.concat([df_equip, nouvel_equip], ignore_index=True)

        # Sauvegarder dans Excel
        from data.data_manager import EQUIPEMENTS_FILE
        df_equip.to_excel(EQUIPEMENTS_FILE, index=False)

        return True, f"✅ Équipement '{id_equipement}' ajouté au département '{departement}'"

    except Exception as e:
        return False, f"❌ Erreur lors de l'ajout : {e}"


def render():
    """Affiche l'onglet Équipements"""

    st.header("📦 Référentiel des Équipements")
    st.caption("Visualisation, ajout et export des équipements par département")

    # Chargement données
    df_equipements = charger_equipements()

    if df_equipements.empty:
        st.warning("⚠️ Aucun équipement trouvé dans le système")
        # Permettre l'ajout même si vide
        df_equipements = pd.DataFrame(columns=['id_equipement', 'departement'])

    # =============================================================================
    # BLOC 0 : AJOUT D'ÉQUIPEMENT
    # =============================================================================

    # =============================================================================
    # BLOC 0 : AJOUT D'ÉQUIPEMENT
    # =============================================================================

    with st.container(border=True):
        st.subheader("➕ Ajouter un nouvel équipement")

        # ✅ SORTIR le radio button HORS du formulaire pour permettre la réactivité
        departements_existants = sorted(df_equipements['departement'].unique()) if not df_equipements.empty else []

        mode_dept = st.radio(
            "Mode département",
            options=["Existant", "Nouveau"],
            horizontal=True,
            key="mode_dept"
        )

        # ✅ Maintenant le formulaire
        with st.form("form_ajout_equipement", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                if mode_dept == "Existant":
                    if departements_existants:
                        departement = st.selectbox(
                            "Département *",
                            options=departements_existants,
                            key="dept_existant"
                        )
                    else:
                        st.warning("Aucun département existant")
                        departement = st.text_input(
                            "Nom du département *",
                            placeholder="Ex: ELECTROLYSE 1",
                            key="dept_nouveau_force"
                        )
                else:  # mode_dept == "Nouveau"
                    departement = st.text_input(
                        "Nom du département *",
                        placeholder="Ex: ELECTROLYSE 1",
                        key="dept_nouveau"
                    )

            with col2:
                id_equipement = st.text_input(
                    "ID Équipement *",
                    placeholder="Ex: 244-3P-1",
                    key="id_equip_nouveau"
                )

            with col3:
                st.write("")  # Espacement
                st.write("")
                submitted = st.form_submit_button(
                    "✅ Ajouter",
                    type="primary",
                    use_container_width=True
                )

            # Validation et enregistrement
            if submitted:
                if not id_equipement.strip():
                    st.error("⚠️ L'ID de l'équipement est requis")
                elif not departement.strip():
                    st.error("⚠️ Le département est requis")
                else:
                    success, message = sauvegarder_equipement(
                        id_equipement.strip(),
                        departement.strip()
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    st.markdown("##")

    # =============================================================================
    # BLOC 1 : TABLEAU ET FILTRES
    # =============================================================================

    with st.container(border=True):
        st.subheader("📋 Liste des équipements")

        if df_equipements.empty:
            st.info("ℹ️ Aucun équipement enregistré. Ajoutez-en un ci-dessus.")
        else:
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

    if not df_equipements.empty:
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

    if not df_equipements.empty:
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