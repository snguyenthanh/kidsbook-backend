# modify database scheme according to the change of models.py
python3 manage.py makemigrations

# apply above migrations
python3 manage.py migrate

if [ $# -ge 1 ]; then
    python3 manage.py runserver $1  # run Django development server on specify port
else
    python3 manage.py runserver  # run Django development server on default port 8080
fi

