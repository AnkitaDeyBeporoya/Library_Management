set -o errexit  

pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate --noinput --settings=library.production
python manage.py collectstatic --noinput --settings=library.production