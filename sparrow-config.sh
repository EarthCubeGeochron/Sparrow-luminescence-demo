here="$(git rev-parse --show-toplevel)"

export SPARROW_PATH="$here/Sparrow"
export SPARROW_LAB_NAME="Desert Research Institute"
export SPARROW_SECRET_KEY="caseinpoint"
export SPARROW_DATA_DIR="$here/test-data"
export SPARROW_COMMANDS="$here/import-pipeline/bin"
export SPARROW_SITE_CONTENT="$here/site-content"
export SPARROW_BACKUP_DIR="$here/db-backups"

# Helps separate database, etc. from other projects'
# artifacts (useful mostly for development)
export COMPOSE_PROJECT_NAME="luminescence"
