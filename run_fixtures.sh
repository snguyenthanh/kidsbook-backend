FIXTURES="fixtures.py"

echo "Deleting existing database."
rm dividesmart/db.sqlite3
echo "Generating new migrations."
python3 dividesmart/manage.py makemigrations
echo "Migrating database."
python3 dividesmart/manage.py migrate
echo "Adding fixtures data from $FIXTURES"
python3 ${FIXTURES}

