"""
Module d'authentification complet
Gestion des utilisateurs avec 4 rôles : Admin, Analyste, Technicien, Autre
"""

import streamlit as st
import os
from supabase import create_client, Client
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from auth.permissions import (
    Permission, 
    has_permission, 
    get_permission_error_message,
    get_role_label,
    get_role_icon,
    get_all_roles
)


# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def get_supabase_client() -> Client:
    """Crée et retourne le client Supabase"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# =============================================================================
# GESTION DE SESSION
# =============================================================================

def init_session_state():
    """Initialise les variables de session si nécessaires"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_departement' not in st.session_state:
        st.session_state.user_departement = None
    # ✅ FIX : initialisation de show_profile manquante
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False


def is_authenticated() -> bool:
    """Vérifie si l'utilisateur est authentifié"""
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[Dict]:
    """Retourne l'utilisateur actuel"""
    if not is_authenticated():
        return None

    return {
        'id': st.session_state.get('user_id'),
        'email': st.session_state.get('user_email'),
        'name': st.session_state.get('user_name'),
        'role': st.session_state.get('user_role'),
        'departement': st.session_state.get('user_departement')
    }


def get_user_role() -> str:
    """Retourne le rôle de l'utilisateur actuel"""
    return st.session_state.get('user_role', 'autre')


def get_user_email() -> str:
    """Retourne l'email de l'utilisateur actuel"""
    return st.session_state.get('user_email', '')


def get_user_name() -> str:
    """Retourne le nom de l'utilisateur actuel"""
    return st.session_state.get('user_name', 'Utilisateur')


# =============================================================================
# VÉRIFICATION DES PERMISSIONS
# =============================================================================

def check_permission(permission: Permission) -> bool:
    """
    Vérifie si l'utilisateur actuel a une permission

    Args:
        permission (Permission): Permission à vérifier

    Returns:
        bool: True si l'utilisateur a la permission
    """
    if not is_authenticated():
        return False

    role = get_user_role()
    return has_permission(role, permission)


def require_permission(permission: Permission, show_error: bool = True) -> bool:
    """
    Vérifie une permission et affiche une erreur si refusé

    Args:
        permission (Permission): Permission requise
        show_error (bool): Afficher un message d'erreur si refusé

    Returns:
        bool: True si autorisé
    """
    if not check_permission(permission):
        if show_error:
            error_msg = get_permission_error_message(permission)
            st.error(error_msg)
            st.info(f"💡 Votre rôle : **{get_role_label(get_user_role())}**")
        return False
    return True


def is_admin() -> bool:
    """Vérifie si l'utilisateur est administrateur"""
    return get_user_role() == 'admin'


def is_analyste() -> bool:
    """Vérifie si l'utilisateur est analyste"""
    return get_user_role() == 'analyste'


def is_technicien() -> bool:
    """Vérifie si l'utilisateur est technicien"""
    return get_user_role() == 'technicien'


# =============================================================================
# AUTHENTIFICATION
# =============================================================================

def login(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Authentifie un utilisateur

    Args:
        email (str): Email de l'utilisateur
        password (str): Mot de passe

    Returns:
        Tuple[success, message, user_data]
    """
    try:
        supabase = get_supabase_client()

        # Tentative de connexion avec Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user:
            # Récupérer les informations complémentaires depuis la table users
            user_info = supabase.table('users')\
                .select('*')\
                .eq('email', email)\
                .eq('actif', True)\
                .single()\
                .execute()

            if not user_info.data:
                # Compte désactivé ou non trouvé
                supabase.auth.sign_out()
                return False, "❌ Compte désactivé ou non autorisé", None

            # Mettre à jour la session
            st.session_state.authenticated = True
            st.session_state.user = response.user
            st.session_state.user_id = user_info.data.get('id')
            st.session_state.user_email = email
            st.session_state.user_role = user_info.data.get('role', 'autre')
            st.session_state.user_name = user_info.data.get('nom_complet', email)
            st.session_state.user_departement = user_info.data.get('departement', '')

            # Enregistrer la dernière connexion et l'action dans l'audit
            try:
                supabase.table('users').update({
                    'derniere_connexion': datetime.now().isoformat()
                }).eq('email', email).execute()

                # Log dans audit
                log_action('connexion', 'users', user_info.data.get('id'), {
                    'email': email,
                    'success': True
                })
            except:
                pass  # Non critique

            role_icon = get_role_icon(st.session_state.user_role)
            role_label = get_role_label(st.session_state.user_role)

            return True, f"✅ Bienvenue {st.session_state.user_name} ! ({role_icon} {role_label})", user_info.data
        else:
            return False, "❌ Identifiants incorrects", None

    except Exception as e:
        error_msg = str(e)

        # Log tentative échouée
        try:
            log_action('tentative_connexion_echouee', 'users', None, {
                'email': email,
                'erreur': error_msg
            })
        except:
            pass

        if "Invalid login credentials" in error_msg:
            return False, "❌ Email ou mot de passe incorrect", None
        elif "Email not confirmed" in error_msg:
            return False, "⚠️ Veuillez confirmer votre email avant de vous connecter", None
        else:
            return False, f"❌ Erreur de connexion : {error_msg}", None


def logout():
    """Déconnecte l'utilisateur"""
    # Log déconnexion
    try:
        if is_authenticated():
            log_action('deconnexion', 'users', st.session_state.get('user_id'), {
                'email': get_user_email()
            })
    except:
        pass

    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except:
        pass

    # Réinitialiser la session
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    init_session_state()
    st.rerun()


# =============================================================================
# GESTION DES UTILISATEURS (ADMIN UNIQUEMENT)
# =============================================================================

def create_user(
    email: str,
    password: str,
    nom_complet: str,
    departement: str = "",
    role: str = "technicien"
) -> Tuple[bool, str]:
    """
    Crée un nouvel utilisateur (admin uniquement)

    Args:
        email (str): Email de l'utilisateur
        password (str): Mot de passe
        nom_complet (str): Nom complet
        departement (str): Département
        role (str): Rôle (admin, analyste, technicien, autre)

    Returns:
        Tuple[success, message]
    """
    if not check_permission(Permission.GERER_UTILISATEURS):
        return False, get_permission_error_message(Permission.GERER_UTILISATEURS)

    try:
        supabase = get_supabase_client()

        # Créer l'utilisateur dans Supabase Auth
        auth_response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True
        })

        if auth_response.user:
            # Ajouter les informations complémentaires dans la table users
            user_data = {
                'user_id': auth_response.user.id,
                'email': email,
                'nom_complet': nom_complet,
                'departement': departement,
                'role': role,
                'actif': True,
                'date_creation': datetime.now().isoformat()
            }

            result = supabase.table('users').insert(user_data).execute()

            # Log action
            log_action('creation_utilisateur', 'users', result.data[0]['id'], {
                'email': email,
                'role': role,
                'created_by': get_user_email()
            })

            role_icon = get_role_icon(role)
            role_label = get_role_label(role)

            return True, f"✅ Utilisateur **{nom_complet}** créé avec succès ({role_icon} {role_label})"
        else:
            return False, "❌ Erreur lors de la création de l'utilisateur"

    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg or "already exists" in error_msg or "duplicate" in error_msg:
            return False, f"⚠️ L'email {email} est déjà utilisé"
        else:
            return False, f"❌ Erreur : {error_msg}"


def get_all_users() -> list:
    """Récupère la liste de tous les utilisateurs (admin uniquement)"""
    if not check_permission(Permission.GERER_UTILISATEURS):
        return []

    try:
        supabase = get_supabase_client()
        result = supabase.table('users')\
            .select('*')\
            .order('date_creation', desc=True)\
            .execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Erreur lors du chargement des utilisateurs : {e}")
        return []


def update_user_role(email: str, new_role: str) -> Tuple[bool, str]:
    """Met à jour le rôle d'un utilisateur (admin uniquement)"""
    if not check_permission(Permission.GERER_UTILISATEURS):
        return False, get_permission_error_message(Permission.GERER_UTILISATEURS)

    try:
        supabase = get_supabase_client()

        supabase.table('users').update({
            'role': new_role
        }).eq('email', email).execute()

        # Log action
        log_action('modification_role', 'users', None, {
            'email': email,
            'nouveau_role': new_role,
            'modified_by': get_user_email()
        })

        role_icon = get_role_icon(new_role)
        role_label = get_role_label(new_role)

        return True, f"✅ Rôle mis à jour : {role_icon} {role_label}"

    except Exception as e:
        return False, f"❌ Erreur : {e}"


def deactivate_user(email: str) -> Tuple[bool, str]:
    """Désactive un utilisateur (admin uniquement)"""
    if not check_permission(Permission.GERER_UTILISATEURS):
        return False, get_permission_error_message(Permission.GERER_UTILISATEURS)

    # Ne pas se désactiver soi-même
    if email == get_user_email():
        return False, "⚠️ Vous ne pouvez pas désactiver votre propre compte"

    try:
        supabase = get_supabase_client()

        supabase.table('users').update({
            'actif': False
        }).eq('email', email).execute()

        # Log action
        log_action('desactivation_utilisateur', 'users', None, {
            'email': email,
            'deactivated_by': get_user_email()
        })

        return True, f"✅ Utilisateur {email} désactivé"

    except Exception as e:
        return False, f"❌ Erreur : {e}"


def reactivate_user(email: str) -> Tuple[bool, str]:
    """Réactive un utilisateur (admin uniquement)"""
    if not check_permission(Permission.GERER_UTILISATEURS):
        return False, get_permission_error_message(Permission.GERER_UTILISATEURS)

    try:
        supabase = get_supabase_client()

        supabase.table('users').update({
            'actif': True
        }).eq('email', email).execute()

        # Log action
        log_action('reactivation_utilisateur', 'users', None, {
            'email': email,
            'reactivated_by': get_user_email()
        })

        return True, f"✅ Utilisateur {email} réactivé"

    except Exception as e:
        return False, f"❌ Erreur : {e}"


def delete_user(email: str) -> Tuple[bool, str]:
    """Supprime définitivement un utilisateur (admin uniquement)"""
    if not check_permission(Permission.GERER_UTILISATEURS):
        return False, get_permission_error_message(Permission.GERER_UTILISATEURS)

    # Ne pas se supprimer soi-même
    if email == get_user_email():
        return False, "⚠️ Vous ne pouvez pas supprimer votre propre compte"

    try:
        supabase = get_supabase_client()

        # Log avant suppression
        log_action('suppression_utilisateur', 'users', None, {
            'email': email,
            'deleted_by': get_user_email()
        })

        # Supprimer de la table users
        supabase.table('users').delete().eq('email', email).execute()

        return True, f"✅ Utilisateur {email} supprimé définitivement"

    except Exception as e:
        return False, f"❌ Erreur : {e}"


# =============================================================================
# RÉINITIALISATION MOT DE PASSE
# =============================================================================

def request_password_reset(email: str) -> Tuple[bool, str]:
    """
    Demande la réinitialisation du mot de passe

    Args:
        email (str): Email de l'utilisateur

    Returns:
        Tuple[success, message]
    """
    try:
        supabase = get_supabase_client()

        # Vérifier que l'utilisateur existe et est actif
        user_check = supabase.table('users')\
            .select('actif')\
            .eq('email', email)\
            .execute()

        if not user_check.data:
            return True, f"✅ Si {email} existe, un email de réinitialisation a été envoyé"

        if not user_check.data[0].get('actif', False):
            return False, "⚠️ Ce compte est désactivé"

        # Envoyer l'email de réinitialisation
        supabase.auth.reset_password_for_email(email, {
            'redirect_to': 'https://votre-app.streamlit.app'  # À adapter
        })

        # Log action
        log_action('demande_reset_password', 'users', None, {
            'email': email
        })

        return True, f"✅ Email de réinitialisation envoyé à {email}"

    except Exception as e:
        return False, f"❌ Erreur : {e}"


def change_password(current_password: str, new_password: str) -> Tuple[bool, str]:
    """Change le mot de passe de l'utilisateur actuel"""
    if not is_authenticated():
        return False, "❌ Non authentifié"

    try:
        supabase = get_supabase_client()
        email = get_user_email()

        # Vérifier le mot de passe actuel
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": current_password
        })

        if not response.user:
            return False, "❌ Mot de passe actuel incorrect"

        # Mettre à jour le mot de passe
        supabase.auth.update_user({
            "password": new_password
        })

        # Log action
        log_action('changement_password', 'users', st.session_state.get('user_id'), {
            'email': email
        })

        return True, "✅ Mot de passe changé avec succès"

    except Exception as e:
        return False, f"❌ Erreur : {e}"


# =============================================================================
# AUDIT LOG
# =============================================================================

def log_action(
    action: str,
    table_name: str,
    record_id: Optional[str],
    details: Optional[Dict[str, Any]] = None
):
    """
    Enregistre une action dans le journal d'audit

    Args:
        action (str): Type d'action (connexion, creation, modification, etc.)
        table_name (str): Nom de la table concernée
        record_id (str): ID de l'enregistrement concerné
        details (dict): Détails supplémentaires
    """
    try:
        if not is_authenticated():
            return

        supabase = get_supabase_client()

        audit_data = {
            'user_id': st.session_state.get('user_id'),
            'email': get_user_email(),
            'action': action,
            'table_name': table_name,
            'record_id': str(record_id) if record_id else None,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }

        supabase.table('audit_log').insert(audit_data).execute()

    except Exception as e:
        print(f"Erreur log audit : {e}")
        pass


def get_audit_logs(limit: int = 100) -> list:
    """Récupère les logs d'audit (admin uniquement)"""
    if not check_permission(Permission.VOIR_AUDIT):
        return []

    try:
        supabase = get_supabase_client()
        result = supabase.table('audit_log')\
            .select('*')\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Erreur chargement audit : {e}")
        return []