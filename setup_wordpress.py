#!/usr/bin/env python3
"""
Script de configuration complète WordPress
Crée les pages et le menu avec la structure du site Jekyll
"""

import mysql.connector
from datetime import datetime

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'horizon',
    'password': 'horizon_password',
    'database': 'horizon_wordpress'
}

# Structure des pages à créer
PAGES = [
    {'title': 'Accueil', 'slug': 'accueil', 'content': '<!-- Contenu de la page d\'accueil -->'},
    {'title': 'Locations', 'slug': 'locations', 'content': '<!-- Page des locations -->'},
    {'title': 'Stages de voile', 'slug': 'stages', 'content': '<!-- Page des stages -->'},
    {'title': 'Info et contact', 'slug': 'contact', 'content': '<!-- Page de contact -->'},
]

# Structure du menu (inspirée de _config.yml)
MENU_STRUCTURE = [
    {'title': 'Home', 'page_slug': 'accueil', 'order': 1, 'parent': None},
    {'title': 'Locations', 'page_slug': 'locations', 'order': 2, 'parent': None},
    {'title': 'Stages voile', 'page_slug': 'stages', 'order': 3, 'parent': None},
    {'title': 'Info et contact', 'page_slug': 'contact', 'order': 4, 'parent': None},
]

def get_db_connection():
    """Crée une connexion à la base de données"""
    return mysql.connector.connect(**DB_CONFIG)

def create_page(cursor, title, slug, content, author_id=1):
    """Crée une page WordPress"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Vérifie si la page existe déjà
    cursor.execute(
        "SELECT ID FROM wp_posts WHERE post_name = %s AND post_type = 'page'",
        (slug,)
    )
    existing = cursor.fetchone()

    if existing:
        print(f"   ⚠️  Page '{title}' existe déjà (ID: {existing[0]})")
        return existing[0]

    # Crée la page en copiant la structure d'une page WordPress par défaut
    cursor.execute("""
        INSERT INTO wp_posts (
            post_author, post_date, post_date_gmt, post_content, post_title,
            post_excerpt, post_status, comment_status, ping_status, post_password,
            post_name, to_ping, pinged, post_modified, post_modified_gmt,
            post_content_filtered, post_parent, guid, menu_order, post_type,
            post_mime_type, comment_count
        ) VALUES (
            %s, %s, %s, %s, %s, %s, 'publish', 'closed', 'closed', '',
            %s, '', '', %s, %s, '', 0, '', 0, 'page', '', 0
        )
    """, (author_id, now, now, content, title, '', slug, now, now))

    post_id = cursor.lastrowid

    # Met à jour le GUID
    cursor.execute(
        "UPDATE wp_posts SET guid = %s WHERE ID = %s",
        (f'http://localhost:8080/?page_id={post_id}', post_id)
    )

    print(f"   ✅ Page '{title}' créée (ID: {post_id})")
    return post_id

def create_menu(cursor, conn):
    """Crée le menu WordPress"""

    # 1. Vérifie si le terme "Menu Principal" existe déjà
    cursor.execute(
        "SELECT term_id FROM wp_terms WHERE name = 'Menu Principal' AND slug = 'menu-principal'"
    )
    existing_term = cursor.fetchone()

    if existing_term:
        print(f"   ⚠️  Menu 'Menu Principal' existe déjà (ID: {existing_term[0]})")
        menu_term_id = existing_term[0]
    else:
        # Crée le terme pour le menu
        cursor.execute(
            "INSERT INTO wp_terms (name, slug) VALUES ('Menu Principal', 'menu-principal')"
        )
        menu_term_id = cursor.lastrowid

        # Associe le terme à la taxonomie nav_menu
        cursor.execute(
            "INSERT INTO wp_term_taxonomy (term_id, taxonomy, description, parent, count) VALUES (%s, 'nav_menu', '', 0, 0)",
            (menu_term_id,)
        )
        menu_taxonomy_id = cursor.lastrowid
        print(f"   ✅ Menu 'Menu Principal' créé (ID: {menu_term_id})")

    # 2. Récupère le term_taxonomy_id
    cursor.execute(
        "SELECT term_taxonomy_id FROM wp_term_taxonomy WHERE term_id = %s AND taxonomy = 'nav_menu'",
        (menu_term_id,)
    )
    menu_taxonomy_id = cursor.fetchone()[0]

    # 3. Enregistre le menu dans les options (pour l'assigner à l'emplacement 'primary')
    cursor.execute(
        "SELECT option_value FROM wp_options WHERE option_name = 'theme_mods_horizon-belleisle'"
    )
    theme_mods = cursor.fetchone()

    if not theme_mods:
        # Crée les theme_mods avec l'emplacement du menu
        import pickle
        theme_mods_data = {
            'nav_menu_locations': {'primary': menu_term_id}
        }
        serialized = pickle.dumps(theme_mods_data).decode('latin-1')

        cursor.execute(
            "INSERT INTO wp_options (option_name, option_value, autoload) VALUES ('theme_mods_horizon-belleisle', %s, 'yes')",
            (serialized,)
        )
    else:
        # Met à jour les theme_mods existants
        print("   💡 Theme mods existent déjà, configurez le menu manuellement dans Apparence > Menus")

    # 4. Crée les items du menu
    print("\n   📝 Création des items du menu...")

    # Récupère les IDs des pages
    page_ids = {}
    for page in PAGES:
        cursor.execute(
            "SELECT ID FROM wp_posts WHERE post_name = %s AND post_type = 'page'",
            (page['slug'],)
        )
        result = cursor.fetchone()
        if result:
            page_ids[page['slug']] = result[0]

    # Crée les items du menu
    for item in MENU_STRUCTURE:
        page_id = page_ids.get(item['page_slug'])
        if not page_id:
            print(f"      ⚠️  Page '{item['page_slug']}' introuvable, item ignoré")
            continue

        # Crée le post pour l'item de menu
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO wp_posts (
                post_author, post_date, post_date_gmt, post_content, post_title,
                post_excerpt, post_status, comment_status, ping_status, post_password,
                post_name, to_ping, pinged, post_modified, post_modified_gmt,
                post_content_filtered, post_parent, guid, menu_order, post_type,
                post_mime_type, comment_count
            ) VALUES (
                1, %s, %s, '', 'navigation', '', 'publish', 'closed', 'closed', '',
                %s, '', '', %s, %s, '', 0, '', %s, 'nav_menu_item', '', 0
            )
        """, (now, now, f'menu-item-{page_id}', now, now, item['order']))

        menu_item_id = cursor.lastrowid

        # Associe l'item au menu
        cursor.execute(
            "INSERT INTO wp_term_relationships (object_id, term_taxonomy_id, term_order) VALUES (%s, %s, %s)",
            (menu_item_id, menu_taxonomy_id, item['order'])
        )

        # Ajoute les métadonnées de l'item
        meta_data = [
            ('_menu_item_type', 'post_type'),
            ('_menu_item_menu_item_parent', '0'),
            ('_menu_item_object_id', str(page_id)),
            ('_menu_item_object', 'page'),
            ('_menu_item_target', ''),
            ('_menu_item_classes', 'a:1:{i:0;s:0:"";}'),
            ('_menu_item_xfn', ''),
            ('_menu_item_url', ''),
        ]

        for meta_key, meta_value in meta_data:
            cursor.execute(
                "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, %s, %s)",
                (menu_item_id, meta_key, meta_value)
            )

        print(f"      ✅ Item '{item['title']}' ajouté au menu")

    # Met à jour le compteur d'items dans le menu
    cursor.execute(
        "UPDATE wp_term_taxonomy SET count = (SELECT COUNT(*) FROM wp_term_relationships WHERE term_taxonomy_id = %s) WHERE term_taxonomy_id = %s",
        (menu_taxonomy_id, menu_taxonomy_id)
    )

    conn.commit()

def main():
    print("🚀 Configuration automatique de WordPress")
    print("=" * 60)

    try:
        # Connexion à la base
        print("\n🔌 Connexion à la base de données...")
        conn = get_db_connection()
        cursor = conn.cursor()
        print("✅ Connecté\n")

        # Création des pages
        print("📄 Création des pages...")
        page_ids = {}
        for page in PAGES:
            page_id = create_page(cursor, page['title'], page['slug'], page['content'])
            page_ids[page['slug']] = page_id

        conn.commit()

        # Configuration de la page d'accueil
        print("\n🏠 Configuration de la page d'accueil...")
        cursor.execute(
            "UPDATE wp_options SET option_value = 'page' WHERE option_name = 'show_on_front'"
        )
        cursor.execute(
            "UPDATE wp_options SET option_value = %s WHERE option_name = 'page_on_front'",
            (page_ids['accueil'],)
        )
        print("✅ Page d'accueil configurée")

        conn.commit()

        # Création du menu
        print("\n📋 Création du menu...")
        create_menu(cursor, conn)

        # Fermeture
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("🎉 Configuration terminée avec succès !")
        print("\n🌐 Visitez http://localhost:8080 pour voir le résultat")
        print("⚙️  Pour configurer le menu : http://localhost:8080/wp-admin/nav-menus.php")

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
