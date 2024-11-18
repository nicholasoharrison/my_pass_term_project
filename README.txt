To run the code ensure you have python version installed: (python version), needs 3.12.1.
Run in terminal two commands: 
pip install -r requirements.txt 
To start the application:
python manage.py runserver


to see updates database schema::
python manage.py makemigrations
python manage.py migrate

trobleshoot:
python manage.py showmigrations MyPassApplication
with db: rm db.sqlite3
and migration procedure again


