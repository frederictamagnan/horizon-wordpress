#!/usr/bin/env python3
"""
Script de migration Jekyll vers WordPress
Lit les fichiers Markdown Jekyll et crée les pages WordPress via SQL
"""

import os
import re
import mysql.connector
from datetime import datetime
from pathlib import Path

# Configuration
JEKYLL_SITE = "/home/ftamagna/codevault/perso/new-website-horizon"
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'horizon',
    'password': 'horizon_password',
    'database': 'horizon_wordpress'
}

# Mapping des slugs Jekyll vers WordPress
PAGE_MAPPING = {
    'index.md': {'slug': 'accueil', 'title': 'Accueil'},
    'contact.md': {'slug': 'contact', 'title': 'Info et contact'},
    'locations.md': {'slug': 'locations', 'title': 'Locations'},
    'stages.md': {'slug': 'stages', 'title': 'Stages de voile'},
    'mentions-legales.md': {'slug': 'mentions-legales', 'title': 'Mentions légales'},
    'plan-site.md': {'slug': 'plan-site', 'title': 'Plan du site'}
}

def parse_front_matter(content):
    """Extrait le front matter YAML et le contenu"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        front_matter = match.group(1)
        body = match.group(2)

        # Parse le titre depuis le front matter
        title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', front_matter)
        title = title_match.group(1) if title_match else None

        return title, body
    return None, content

def create_wordpress_page(cursor, title, slug, content, author_id=1):
    """Crée une page WordPress dans la base de données"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insertion du post
    post_query = """
    INSERT INTO wp_posts
    (post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt,
     post_status, comment_status, ping_status, post_name, to_ping, pinged,
     post_modified, post_modified_gmt, post_parent, menu_order, post_type, comment_count)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    post_values = (
        author_id,           # post_author
        now,                 # post_date
        now,                 # post_date_gmt
        content,             # post_content
        title,               # post_title
        '',                  # post_excerpt
        'publish',           # post_status
        'closed',            # comment_status
        'closed',            # ping_status
        slug,                # post_name (slug)
        '',                  # to_ping
        '',                  # pinged
        now,                 # post_modified
        now,                 # post_modified_gmt
        0,                   # post_parent
        0,                   # menu_order
        'page',              # post_type
        0                    # comment_count
    )

    cursor.execute(post_query, post_values)
    return cursor.lastrowid

def main():
    print("🚀 Démarrage de la migration Jekyll → WordPress")
    print(f"📂 Source: {JEKYLL_SITE}")

    # Connexion à la base de données via Docker
    print("\n🔌 Connexion à la base de données...")
    try:
        # On se connecte via le port exposé du conteneur
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Connecté à la base de données")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("\n💡 Astuce: Assurez-vous que le port 3306 est exposé dans docker-compose.yml")
        print("   Ajoutez sous le service 'db': ports: - \"3306:3306\"")
        return

    # Traitement des fichiers
    migrated = 0
    for filename, page_info in PAGE_MAPPING.items():
        filepath = Path(JEKYLL_SITE) / filename

        if not filepath.exists():
            print(f"⚠️  Fichier non trouvé: {filename}")
            continue

        print(f"\n📄 Migration de {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse le front matter
        fm_title, body = parse_front_matter(content)
        title = fm_title or page_info['title']

        # Vérifie si la page existe déjà
        cursor.execute(
            "SELECT ID FROM wp_posts WHERE post_name = %s AND post_type = 'page'",
            (page_info['slug'],)
        )
        existing = cursor.fetchone()

        if existing:
            print(f"   ⚠️  Page '{title}' existe déjà (ID: {existing[0]}), mise à jour...")
            cursor.execute(
                "UPDATE wp_posts SET post_content = %s, post_title = %s WHERE ID = %s",
                (body, title, existing[0])
            )
        else:
            print(f"   ✨ Création de la page '{title}'...")
            post_id = create_wordpress_page(cursor, title, page_info['slug'], body)
            print(f"   ✅ Page créée (ID: {post_id})")

        migrated += 1

    # Commit et fermeture
    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n🎉 Migration terminée ! {migrated} page(s) migrée(s)")
    print("\n🌐 Visitez http://localhost:8080 pour voir le résultat")

if __name__ == "__main__":
    main()
