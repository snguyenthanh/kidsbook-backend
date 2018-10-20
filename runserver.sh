source run_fixtures.sh


if [ $# -ge 1 ]; then
    python3 manage.py runserver $1  # run Django development server on specify port
else
    python3 manage.py runserver  # run Django development server on default port 8000
fi
