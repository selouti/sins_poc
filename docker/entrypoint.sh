#!/usr/bin/env sh
set -e

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-sins.settings}

# Install DB migrations
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput

# Collect static (ignored if none)
python manage.py collectstatic --noinput || true

# Optionally load sample data
if [ "${LOAD_SAMPLE_DATA}" = "1" ]; then
  echo "Loading sample data via management command..."
  python manage.py load_sample_data || true
fi

exec "$@"
