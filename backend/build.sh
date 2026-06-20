#!/usr/bin/env bash
# Render build step: install, collect static, migrate, seed plans, ensure admin.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py seed_plans
python manage.py ensure_superuser
