"""
Page de connexion professionnelle
Design moderne et attractif avec logo, animations et branding
"""

import streamlit as st
from auth.auth import (
    login, logout, is_authenticated, init_session_state,
    request_password_reset, get_user_name, get_user_email,
    get_user_role
)
from auth.permissions import get_role_icon, get_role_label, get_role_color


# =============================================================================
# STYLES CSS PERSONNALISÉS
# =============================================================================

def inject_custom_css():
    """Injecte du CSS personnalisé pour un design professionnel"""
    st.markdown("""
        <style>

        /* ── Fond de page entière en dégradé violet ── */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            min-height: 100vh;
        }

        /* Cacher le header Streamlit */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* ── Carte blanche centrale ── */
        .login-card {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        /* ── Logo et titre (sur fond violet, donc blanc) ── */
        .logo-container {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .logo-icon {
            font-size: 4rem;
            animation: pulse 2s infinite;
            display: block;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .app-title {
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0.5rem 0 0.3rem 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .app-subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            font-weight: 300;
        }

        /* ── Labels des champs (fond blanc → texte foncé) ── */
        .stTextInput label,
        .stTextInput label p,
        div[data-testid="stTextInput"] label,
        div[data-testid="stTextInput"] label p {
            color: #2d2d2d !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }

        /* ── Champs input ── */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            background: #fafafa;
            font-size: 1rem;
            padding: 0.75rem;
            color: #2d2d2d !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102,126,234,0.2);
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background-color: #f0f0f5;
            padding: 0.4rem;
            border-radius: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            font-weight: 600;
        }

        /* Texte des onglets : foncé sur fond clair */
        .stTabs [data-baseweb="tab"] p,
        .stTabs [data-baseweb="tab"] span,
        .stTabs [data-baseweb="tab"] div,
        .stTabs [data-baseweb="tab"] button {
            color: #444 !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] span {
            color: #667eea !important;
        }

        /* ── Boutons ── */
        .stButton > button {
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        }

        /* ── Footer (sur fond violet) ── */
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255,255,255,0.3);
        }

        /* ── Messages ── */
        .stAlert {
            border-radius: 10px;
        }

        /* ── Badge rôle ── */
        .role-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
            margin: 0.5rem 0;
        }

        </style>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE DE CONNEXION
# =============================================================================

def render_login_page():
    """Affiche la page de connexion professionnelle"""

    init_session_state()

    if is_authenticated():
        return

    inject_custom_css()

    # Logo et titre sur le fond violet (hors carte blanche)
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:

        st.markdown('''
            <div class="logo-container">
                <span class="logo-icon">🏭</span>
                <h1 class="app-title">MaintenancePro</h1>
                <p class="app-subtitle">Système de Gestion Industrielle</p>
            </div>
        ''', unsafe_allow_html=True)

        # Carte blanche pour le formulaire
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Connexion", "🔑 Mot de passe oublié"])

        # =====================================================================
        # ONGLET CONNEXION
        # =====================================================================
        with tab1:

            with st.form("login_form", clear_on_submit=False):
                email = st.text_input(
                    "📧 Adresse email professionnelle",
                    placeholder="votre.email@entreprise.com",
                    key="login_email",
                    help="Utilisez votre email professionnel fourni par l'administrateur"
                )

                password = st.text_input(
                    "🔒 Mot de passe",
                    type="password",
                    placeholder="••••••••",
                    key="login_password",
                    help="Minimum 8 caractères"
                )

                col_space, col_btn = st.columns([1, 2])
                with col_btn:
                    submitted = st.form_submit_button(
                        "🚀 Se connecter",
                        type="primary",
                        use_container_width=True
                    )

                if submitted:
                    if not email or not password:
                        st.error("⚠️ Veuillez remplir tous les champs")
                    elif "@" not in email:
                        st.error("⚠️ Format d'email invalide")
                    else:
                        with st.spinner("🔄 Authentification en cours..."):
                            success, message, user_data = login(email.lower().strip(), password)

                            if success:
                                st.success(message)
                                st.balloons()
                                import time
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(message)
                                if "incorrect" in message.lower():
                                    st.info("💡 **Conseils :**\n\n"
                                            "• Vérifiez les majuscules/minuscules\n"
                                            "• Assurez-vous de ne pas avoir CAPS LOCK activé\n"
                                            "• Utilisez 'Mot de passe oublié' si nécessaire")

        # =====================================================================
        # ONGLET MOT DE PASSE OUBLIÉ
        # =====================================================================
        with tab2:
            st.info("📧 Un lien de réinitialisation sera envoyé à votre adresse email")

            with st.form("reset_password_form"):

                reset_email = st.text_input(
                    "📧 Votre adresse email professionnelle",
                    placeholder="votre.email@entreprise.com",
                    key="reset_email"
                )

                col_space, col_btn_reset = st.columns([1, 2])
                with col_btn_reset:
                    reset_submitted = st.form_submit_button(
                        "📤 Envoyer le lien",
                        type="secondary",
                        use_container_width=True
                    )

                if reset_submitted:
                    if not reset_email:
                        st.error("⚠️ Veuillez entrer votre email")
                    elif "@" not in reset_email:
                        st.error("⚠️ Format d'email invalide")
                    else:
                        with st.spinner("📨 Envoi en cours..."):
                            success, message = request_password_reset(reset_email.lower().strip())

                            if success:
                                st.success(message)
                                st.info("✅ **Prochaines étapes :**\n\n"
                                        "1. Vérifiez votre boîte de réception\n"
                                        "2. Cliquez sur le lien reçu\n"
                                        "3. Créez votre nouveau mot de passe\n\n"
                                        "⏰ Le lien expire dans 1 heure")

                                with st.expander("📮 Email non reçu ?"):
                                    st.markdown("""
                                    **Vérifiez :**
                                    - Votre dossier SPAM/Courrier indésirable
                                    - L'orthographe de votre email
                                    - Que votre compte est bien actif

                                    **Toujours rien ?**
                                    Contactez votre administrateur système
                                    """)
                            else:
                                st.error(message)

        st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================================
        # SECTION AIDE ET SUPPORT
        # =====================================================================
        with st.expander("❓ Besoin d'aide ?"):
            col_help1, col_help2 = st.columns(2)

            with col_help1:
                st.markdown("""\
**🔐 Problèmes de connexion**
• Email ou mot de passe incorrect\n
• Compte désactivé\n
• Email non confirmé\n
→ Utilisez "Mot de passe oublié"
""")

            with col_help2:
                st.markdown("""\
**👤 Nouveau utilisateur**

• Contactez votre responsable\n
• Demandez la création d'un compte\n
• Un admin vous enverra vos identifiants\n
→ Changez votre mot de passe après la 1ère connexion
""")

            st.markdown("---")

            st.markdown("""
**📞 Support Technique**

- **Email :** zaravitamds18@gmail.com
- **Tél :** +212 77 06 362 97
- **Heures :** Lun-Ven 8h00-17h00

*Temps de réponse moyen : 2 heures*
""")

        # =====================================================================
        # FOOTER
        # =====================================================================
        st.markdown('''
            <div class="footer">
                <p>🔒 Connexion sécurisée par chiffrement SSL</p>
                <p>© 2025 Votre Entreprise SA • Tous droits réservés</p>
                <p style="font-size: 0.8rem; margin-top: 0.5rem;">
                    Version 2.0.0 • Développé avec ❤️ au Maroc
                </p>
            </div>
        ''', unsafe_allow_html=True)


# =============================================================================
# INFORMATIONS UTILISATEUR
# =============================================================================

def render_user_info():
    """
    - Popover profil + déconnexion en haut à droite (dans la page principale)
    - Rôle discret en bas de la sidebar
    """
    if not is_authenticated():
        return

    inject_custom_css()

    user_name  = get_user_name()
    user_email = get_user_email()
    user_role  = get_user_role()
    user_dept  = st.session_state.get('user_departement', '')

    role_icon  = get_role_icon(user_role)
    role_label = get_role_label(user_role)
    role_color = get_role_color(user_role)

    _, col_pop = st.columns([11, 1])
    with col_pop:
        with st.popover(f"{role_icon}", use_container_width=False):
            st.markdown(
                f"<div style='text-align:center; font-size:2.5rem; margin-bottom:0.3rem'>"
                f"{role_icon}</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='background:{role_color}; color:white; text-align:center; "
                f"padding:0.3rem 0.8rem; border-radius:20px; font-weight:600; "
                f"font-size:0.85rem; margin-bottom:0.8rem'>{role_label}</div>",
                unsafe_allow_html=True
            )
            st.markdown(f"**{user_name}**")
            st.caption(f"📧 {user_email}")
            if user_dept:
                st.caption(f"🏢 {user_dept}")

            st.markdown("---")

            if st.button("👤 Mon profil", use_container_width=True, key="btn_profile_pop"):
                st.session_state.show_profile = not st.session_state.get('show_profile', False)
                st.rerun()

            if st.button("🚪 Déconnexion", use_container_width=True,
                         type="secondary", key="btn_logout_pop"):
                logout()

    with st.sidebar:
        st.markdown(
            "<div style='position:fixed; bottom:1rem; left:0; width:18rem; "
            "padding:0 1rem; box-sizing:border-box;'>"
            f"<div style='background:{role_color}20; border:1px solid {role_color}40; "
            f"border-radius:10px; padding:0.5rem 0.8rem; text-align:center; "
            f"font-size:0.82rem; color:{role_color}; font-weight:600;'>"
            f"{role_icon} {role_label} • {user_name}"
            "</div></div>",
            unsafe_allow_html=True
        )

    if st.session_state.get('show_profile', False):
        render_profile_modal()


# =============================================================================
# MODAL PROFIL UTILISATEUR
# =============================================================================

def render_profile_modal():
    """Affiche le profil utilisateur avec option changement de mot de passe"""

    st.markdown("---")
    st.subheader("👤 Mon Profil")

    user_name  = get_user_name()
    user_email = get_user_email()
    user_role  = get_user_role()
    user_dept  = st.session_state.get('user_departement', '')

    user = st.session_state.get("user", None)
    derniere_co = "N/A"
    if user is not None:
        derniere_co = getattr(user, "last_sign_in_at", "N/A")

    st.write(f"**Nom :** {user_name}")
    st.write(f"**Email :** {user_email}")
    st.write(f"**Rôle :** {get_role_icon(user_role)} {get_role_label(user_role)}")
    if user_dept:
        st.write(f"**Département :** {user_dept}")

    st.markdown("##")

    with st.expander("🔒 Changer mon mot de passe"):
        with st.form("change_password_form"):
            current_pwd = st.text_input("Mot de passe actuel",    type="password", key="current_pwd")
            new_pwd     = st.text_input("Nouveau mot de passe",   type="password", key="new_pwd")
            confirm_pwd = st.text_input("Confirmer le nouveau",   type="password", key="confirm_pwd")

            submitted = st.form_submit_button("✅ Changer", type="primary")

            if submitted:
                if not current_pwd or not new_pwd or not confirm_pwd:
                    st.error("⚠️ Tous les champs sont requis")
                elif new_pwd != confirm_pwd:
                    st.error("⚠️ Les nouveaux mots de passe ne correspondent pas")
                elif len(new_pwd) < 8:
                    st.error("⚠️ Le mot de passe doit contenir au moins 8 caractères")
                else:
                    from auth.auth import change_password
                    success, message = change_password(current_pwd, new_pwd)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    if st.button("✖️ Fermer", use_container_width=True):
        st.session_state.show_profile = False
        st.rerun()