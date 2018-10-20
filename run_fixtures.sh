FIXTURES="fixtures.py"
rm db.sqlite3
rm -r kidsbook/migrations
echo "Deleting existing database."
psql -d app_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public;"
echo "Generating new migrations."
python3 manage.py makemigrations kidsbook
echo "Migrating database."
python3 manage.py migrate
echo "Adding fixtures data from $FIXTURES"
python3 ${FIXTURES}
