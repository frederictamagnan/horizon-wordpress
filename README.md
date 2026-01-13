# Horizon Belle-Isle - Version WordPress

Ce dossier contient le thème WordPress personnalisé pour l'école de voile Horizon Belle-Isle.

## Installation locale avec Docker Compose (Recommandé)

### Prérequis
- Docker et Docker Compose installés
- Port 8080 disponible

### Démarrage rapide

1. **Lancer les conteneurs** :
```bash
cd /home/ftamagna/codevault/perso/horizon-wordpress
docker compose up -d
```

2. **Accéder à WordPress** :
- Site : http://localhost:8080
- Première visite : l'installation WordPress se lance automatiquement

3. **Configurer WordPress** :
- Langue : Français
- Titre du site : `Horizon Belle-Isle`
- Identifiant admin : (à votre choix)
- Mot de passe : (à votre choix)
- Email : (votre email)

4. **Arrêter les conteneurs** :
```bash
docker compose down
```

5. **Supprimer tout (y compris la base de données)** :
```bash
docker compose down -v
```

### Base de données
- **Host** : db:3306
- **Database** : horizon_wordpress
- **User** : horizon
- **Password** : horizon_password

## Installation sur LWS (Production)

1. Connectez-vous à votre panneau LWS
2. Installez WordPress via l'installateur automatique
3. Uploadez le dossier `wp-content/themes/horizon-belleisle/` via FTP

### 2. Configuration WordPress

1. Accédez à l'interface d'administration WordPress
2. Allez dans **Apparence > Thèmes**
3. Activez le thème **Horizon Belle-Isle**

### 3. Créer les pages

Créez les pages suivantes dans **Pages > Ajouter** :

#### Page d'accueil (Accueil)
- Titre : `Accueil`
- Type : Page d'accueil (voir Réglages > Lecture)
- Contenu : Laissez vide, le contenu est géré par le template `front-page.php`

#### Page Locations
- Titre : `Locations`
- Slug : `locations`
- Contenu : Voir fichier `pages-content/locations.html`

#### Page Stages voile
- Titre : `Stages voile`
- Slug : `stages`
- Contenu : Voir fichier `pages-content/stages.html`

#### Page Info et contact
- Titre : `Info et contact`
- Slug : `info-et-contact`
- Contenu : Voir fichier `pages-content/contact.html`
- Champ personnalisé : `hero_subtitle` = "Toutes les informations pour nous rejoindre"

#### Page Mentions légales
- Titre : `Mentions légales`
- Slug : `mentions-legales`
- Contenu : Voir fichier `pages-content/mentions-legales.html`

### 4. Configurer le menu

1. Allez dans **Apparence > Menus**
2. Créez un nouveau menu appelé "Menu Principal"
3. Ajoutez les pages dans cet ordre :
   - Accueil
   - Locations (avec sous-menus)
     - Hobbie Cat (lien vers `/locations/#hobbie-cat`)
     - Planche à voile (lien vers `/locations/#planche-voile`)
     - Paddle (lien vers `/locations/#paddle`)
     - Moteur (lien vers `/locations/#moteur`)
     - Kayak (lien vers `/locations/#kayak`)
   - Stages voile
   - Info et contact
4. Assignez le menu à l'emplacement "Menu Principal"

### 5. Configuration du site

Allez dans **Réglages > Général** :
- Titre du site : `Horizon Belle-Isle`
- Slogan : `École de voile à Belle-Isle`

Allez dans **Réglages > Lecture** :
- La page d'accueil affiche : Une page statique
- Page d'accueil : Accueil

### 6. Ajouter les images

Les images sont déjà dans le dossier `wp-content/themes/horizon-belleisle/images/` :
- `logo.png` - Logo Horizon
- `ffv.jpg` - Logo FFVoile

Pour ajouter un logo personnalisé dans WordPress :
1. Allez dans **Apparence > Personnaliser > Identité du site**
2. Uploadez `logo.png`

## Déploiement sur LWS

### Via FTP
1. Connectez-vous en FTP à votre hébergement LWS
2. Uploadez tout le contenu du dossier `horizon-wordpress/` dans le dossier racine de votre site
3. Configurez la base de données MySQL via le panneau LWS
4. Accédez à votre site et suivez l'installation WordPress

### Via l'installateur LWS
1. Installez WordPress via le panneau LWS (installation en 1 clic)
2. Uploadez uniquement le dossier `wp-content/themes/horizon-belleisle/` via FTP
3. Activez le thème dans l'administration WordPress
4. Créez les pages et le menu comme indiqué ci-dessus

## Structure du thème

```
horizon-belleisle/
├── style.css           # Styles principaux (obligatoire)
├── functions.php       # Fonctions du thème
├── header.php          # En-tête
├── footer.php          # Pied de page
├── index.php           # Template par défaut
├── page.php            # Template pour les pages
├── front-page.php      # Template pour la page d'accueil
├── images/             # Images du thème
│   ├── logo.png
│   └── ffv.jpg
└── pages-content/      # Contenu HTML des pages
    ├── locations.html
    ├── stages.html
    ├── contact.html
    └── mentions-legales.html
```

## Support

Pour toute question, consultez :
- Documentation WordPress FR : https://fr.wordpress.org/support/
- Documentation LWS : https://aide.lws.fr/
