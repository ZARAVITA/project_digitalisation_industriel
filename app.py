
"""
Application Streamlit - Gestion des Rapports de Maintenance
Version avec authentification complète - navigation sidebar
"""
import streamlit as st
from ui import equipements, observations, telechargements, modifications, suppressions
from data.data_manager import initialiser_fichiers
from auth.auth import init_session_state, is_authenticated, check_permission
from auth.login_page import render_login_page, render_user_info
from auth.permissions import Permission

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="MaintenancePro",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# INITIALISATION
# =============================================================================

init_session_state()
initialiser_fichiers()

# =============================================================================
# INTERFACE PRINCIPALE
# =============================================================================

def main():
    """Point d'entrée principal"""

    # Vérifier authentification
    if not is_authenticated():
        render_login_page()
        st.stop()

    # Afficher profil (icône top-right + sidebar bas)
    render_user_info()

    # En-tête avec icône profil à droite
    col_title, col_profile = st.columns([8, 1])
    with col_title:
        st.title("🏭 MaintenancePro - Gestion Industrielle")
        st.caption("Système de suivi des équipements et observations")
    st.markdown("---")

    # =============================================================================
    # NAVIGATION SIDEBAR EN HAUT
    # =============================================================================

    with st.sidebar:
        st.markdown("### 📌 Navigation")
        st.markdown("---")

    pages = {
        "📦 Équipements":   Permission.VOIR_EQUIPEMENTS,
        "📝 Observations":  Permission.VOIR_OBSERVATIONS,
        "📥 Exports":       Permission.EXPORTER_DONNEES,
        "✏️ Modifications": Permission.MODIFIER_OBSERVATIONS,
        "🗑️ Suppressions":  Permission.SUPPRIMER_OBSERVATIONS,
    }

    pages_accessibles = [
        nom for nom, perm in pages.items()
        if check_permission(perm)
    ]

    if not pages_accessibles:
        st.error("🔒 Aucune page accessible avec votre rôle.")
        st.stop()

    if "page_active" not in st.session_state:
        st.session_state.page_active = pages_accessibles[0]

    with st.sidebar:
        for nom_page in pages_accessibles:
            is_active = st.session_state.page_active == nom_page
            if st.button(
                nom_page,
                key=f"nav_{nom_page}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.page_active = nom_page
                st.rerun()

    # =============================================================================
    # AFFICHAGE DE LA PAGE ACTIVE
    # =============================================================================

    page = st.session_state.page_active

    if page == "📦 Équipements":
        equipements.render()
    elif page == "📝 Observations":
        observations.render()
    elif page == "📥 Exports":
        telechargements.render()
    elif page == "✏️ Modifications":
        modifications.render()
    elif page == "🗑️ Suppressions":
        suppressions.render()


if __name__ == "__main__":
    main()
