# Guide de Migration vers LWS

## Prérequis
- Accès à l'explorateur de fichiers LWS (FTP ou File Manager)
- Accès à phpMyAdmin sur LWS
- Base de données MySQL créée sur LWS

## Étape 1 : Export de la base de données locale

```bash
./export_database.sh
```

Ce script va créer un fichier `wordpress_export_YYYYMMDD_HHMMSS.sql` avec toute la base de données.

**Alternative manuelle :**
```bash
docker exec horizon-wordpress-db-1 mysqldump -uwordpress -pwordpress wordpress > wordpress_export.sql
```

## Étape 2 : Préparation des fichiers

Les fichiers à copier sur LWS :
- `wp-content/themes/horizon-belleisle/` (tout le dossier du thème)
- `wp-content/languages/` (fichiers de traduction française)

**Note :** WordPress core (wp-admin, wp-includes) est déjà installé sur LWS, pas besoin de le copier.

## Étape 3 : Import de la base de données sur LWS

1. Connecte-toi à **phpMyAdmin** sur ton hébergement LWS
2. Sélectionne ta base de données (ou crée-en une nouvelle)
3. Va dans l'onglet **"Importer"**
4. Choisis le fichier `.sql` exporté à l'étape 1
5. Clique sur **"Exécuter"**

⚠️ **Important :** Si tu as déjà des tables WordPress, il faut les supprimer avant l'import, ou bien cocher "DROP TABLE IF EXISTS" lors de l'export.

## Étape 4 : Upload des fichiers du thème

Via l'explorateur de fichiers LWS :
1. Va dans le dossier `wp-content/themes/`
2. Upload tout le dossier `horizon-belleisle/`
3. Vérifie que tous les sous-dossiers sont présents :
   - `css/components/`
   - `images/`
   - `pages-content/`
   - Les fichiers PHP à la racine

## Étape 5 : Configuration wp-config.php

Sur LWS, édite le fichier `wp-config.php` avec les informations de connexion fournies par LWS :

```php
define('DB_NAME', 'nom_base_lws');
define('DB_USER', 'utilisateur_lws');
define('DB_PASSWORD', 'mot_de_passe_lws');
define('DB_HOST', 'localhost'); // ou l'hôte fourni par LWS
```

## Étape 6 : Mise à jour des URLs (si nécessaire)

Si ton site passe de `localhost:8080` à `horizon-belleisle.fr`, il faut mettre à jour les URLs dans la base de données.

**Via phpMyAdmin :**
```sql
UPDATE wp_options SET option_value = 'https://horizon-belleisle.fr' WHERE option_name = 'siteurl';
UPDATE wp_options SET option_value = 'https://horizon-belleisle.fr' WHERE option_name = 'home';
```

**OU via un plugin :** Installe le plugin "Better Search Replace" depuis wp-admin pour remplacer toutes les occurrences.

## Étape 7 : Vérifications

1. Accède à `https://ton-domaine.fr`
2. Vérifie que le thème s'affiche correctement
3. Teste la navigation (menu, pages, actualités)
4. Vérifie les images et styles CSS
5. Teste l'admin : `https://ton-domaine.fr/wp-admin`

## Problèmes courants

### Les CSS ne se chargent pas
- Vide le cache du navigateur (Ctrl+F5)
- Vérifie les permissions des fichiers (644 pour les fichiers, 755 pour les dossiers)
- Vérifie que le dossier `css/components/` est bien uploadé

### Erreur de connexion à la base de données
- Vérifie les informations dans wp-config.php
- Vérifie que la base de données est bien créée sur LWS
- Vérifie que l'utilisateur a les droits sur cette base

### Le site affiche le thème par défaut
- Active le thème "Horizon Belle-Isle" depuis wp-admin > Apparence > Thèmes
- Ou via SQL :
```sql
UPDATE wp_options SET option_value = 'horizon-belleisle' WHERE option_name = 'template';
UPDATE wp_options SET option_value = 'horizon-belleisle' WHERE option_name = 'stylesheet';
```

### Les permalinks ne fonctionnent pas
- Va dans wp-admin > Réglages > Permaliens
- Re-enregistre la structure (clic sur "Enregistrer" sans rien changer)
- Vérifie que le fichier `.htaccess` existe et est modifiable

## Checklist finale

- [ ] Base de données importée
- [ ] Thème uploadé dans wp-content/themes/
- [ ] wp-config.php configuré avec les infos LWS
- [ ] URLs mises à jour (si domaine différent)
- [ ] Site accessible et fonctionnel
- [ ] Admin accessible (wp-admin)
- [ ] Navigation et menu fonctionnels
- [ ] Page Actualités fonctionne
- [ ] CSS et images chargent correctement
- [ ] Footer avec lien Instagram présent

## Scripts SQL utiles

### Réinitialiser le mot de passe admin
```sql
UPDATE wp_users SET user_pass = MD5('nouveau_mot_de_passe') WHERE user_login = 'admin';
```

### Vérifier le thème actif
```sql
SELECT * FROM wp_options WHERE option_name IN ('template', 'stylesheet');
```

### Lister toutes les pages
```sql
SELECT ID, post_title, post_name, post_status FROM wp_posts WHERE post_type = 'page';
```
