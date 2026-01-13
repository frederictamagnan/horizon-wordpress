#!/bin/bash
# Export de la base de données WordPress pour migration vers LWS

# Charger les variables depuis .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ Fichier .env non trouvé"
    exit 1
fi

# Variables
DB_NAME="${MYSQL_DATABASE}"
DB_USER="${MYSQL_USER}"
DB_PASSWORD="${MYSQL_PASSWORD}"
CONTAINER_NAME="${CONTAINER_NAME:-horizon-db}"

# Nom du fichier de sortie
OUTPUT_FILE="wordpress_export_$(date +%Y%m%d_%H%M%S).sql"

echo "Export de la base de données WordPress..."

# Export via docker exec
docker exec $CONTAINER_NAME mysqldump -u$DB_USER -p$DB_PASSWORD $DB_NAME > $OUTPUT_FILE

if [ $? -eq 0 ]; then
    echo "✅ Export réussi : $OUTPUT_FILE"
    echo ""
    echo "Étapes suivantes pour la migration LWS :"
    echo "1. Télécharge le fichier $OUTPUT_FILE"
    echo "2. Va sur phpMyAdmin LWS"
    echo "3. Sélectionne ta base de données"
    echo "4. Onglet 'Importer' > Choisis le fichier .sql"
    echo "5. Upload les fichiers du thème wp-content/themes/horizon-belleisle/ via FTP/explorateur"
    echo "6. Modifie wp-config.php avec les infos de connexion LWS"
else
    echo "❌ Erreur lors de l'export"
    exit 1
fi
