source venv/bin/activate
git pull
pkill -f gunicorn
gunicorn --bind 127.0.0.1:8000 -m 000 wsgi:app --log-file log >> out &
