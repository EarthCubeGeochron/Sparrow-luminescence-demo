here="${0:h}"

export SPARROW_PATH="$here/Sparrow"
export SPARROW_LAB_NAME="Desert Research Institute"
export SPARROW_DATA_DIR="$here/test-data"
export SPARROW_COMMANDS="$here/import-pipeline/bin"
export SPARROW_SITE_CONTENT="$here/site-content"
export SPARROW_BACKUP_DIR="$here/db-backups"

# SPARROW_ENV="production" modifies the app's configuration
# to run under Docker's "unless-stopped" restart policy, which
# keeps the application up through system reboots (if the underlying
# Docker Engine is restarted with systemd
export SPARROW_ENV="production"

# Override docker-compose to add SSL config
export SPARROW_COMPOSE_OVERRIDES="-f $(pwd)/docker-compose.ssl.yaml"

# An override file for application secrets
secrets="$here/sparrow-secrets.sh"
if [ -f $secrets ]; then
  source $secrets
else
  echo "Please create file 'sparrow-secrets.sh' using the template 'sparrow-secrets.example.sh'"
fi

# A separate overrides file if we want to define specific variables for production
overrides="$here/sparrow-config.overrides.sh"
[ -f "$overrides" ] && source "$overrides"

# Helps separate database, etc. from other projects'
# artifacts (useful mostly for development)
export COMPOSE_PROJECT_NAME="luminescence"
