FIXTURES="fixtures.py"

echo "Deleting existing database."
rm db.sqlite3
echo "Generating new migrations."
python3 manage.py makemigrations kidsbook
echo "Migrating database."
python3 manage.py migrate
echo "Adding fixtures data from $FIXTURES"
python3 ${FIXTURES}
