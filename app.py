"""
Application Streamlit - Gestion des Rapports de Maintenance
Version refactorisée avec navigation par onglets
"""

import streamlit as st
from ui import equipements, observations, telechargements, suppressions
from data.data_manager import initialiser_fichiers

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Rapport Maintenance",
    page_icon="🔧",
    layout="wide"
)

# =============================================================================
# INITIALISATION
# =============================================================================

# Créer les fichiers de données au démarrage si nécessaire
initialiser_fichiers()

# =============================================================================
# INTERFACE PRINCIPALE
# =============================================================================



def main():
    """Point d'entrée principal de l'application"""

    # En-tête
    st.title("🔧 Gestion des rapports de Maintenance")
    st.caption("Système de suivi des équipements et observations")
    st.markdown("---")

    # Navigation par onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Équipements",
        "📝 Observations",
        "📥 Téléchargements",
        "🗑️ Suppressions"
    ])

    with tab1:
        equipements.render()

    with tab2:
        observations.render()

    with tab3:
        telechargements.render()

    with tab4:
        suppressions.render()


if __name__ == "__main__":
    main()