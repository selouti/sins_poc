#!/usr/bin/env sh
set -e

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-sins.settings}

# Install DB migrations
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput

# Collect static (ignored if none)
python manage.py collectstatic --noinput || true

# Optionally load sample data (accept common truthy values)
LOAD_FLAG="${LOAD_SAMPLE_DATA:-${load_sample_data:-}}"
LOWER_FLAG=$(printf "%s" "$LOAD_FLAG" | tr '[:upper:]' '[:lower:]')
if [ "$LOWER_FLAG" = "1" ] || [ "$LOWER_FLAG" = "true" ] || [ "$LOWER_FLAG" = "yes" ] || [ "$LOWER_FLAG" = "on" ]; then
  echo "[entrypoint] LOAD_SAMPLE_DATA=$LOAD_FLAG → running python manage.py load_sample_data"
  python manage.py load_sample_data || true
else
  echo "[entrypoint] LOAD_SAMPLE_DATA not set to a truthy value (got: '${LOAD_FLAG}'); skipping sample data load"
fi

exec "$@"
