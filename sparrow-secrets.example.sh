# Sparrow's secret key is used to salt passwords and provide server security.
# If it is changed, all passwords and API tokens will need to be reissued.
export SPARROW_SECRET_KEY="this is secret"

# Mapbox is used for maps by the default Sparrow site.
# The Mapbox API requires an _access token_ to ensure that accounts abide
# by the initial free limits or pay for overuse.
# Get a token at https://account.mapbox.com/access-tokens
export MAPBOX_API_TOKEN="YOUR TOKEN HERE"
