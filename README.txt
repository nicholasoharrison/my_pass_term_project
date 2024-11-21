To run the code ensure you have python version installed: (python version), needs 3.12.1.
Run in terminal two commands: 
pip install -r requirements.txt

to activate encryption library:
pip install cryptography
in terminal type : cd /workspaces/my_pass_term_project/MyPass
-> python generate_encription_key.py
Run this script once, and it will print out the key. Copy that key and store it securely in your Django settings.
 you can also use .env file and store it there


To start the application:
python manage.py runserver


to see updates database schema::
python manage.py makemigrations
python manage.py migrate

trobleshoot:
python manage.py showmigrations MyPassApplication
with db: rm db.sqlite3
and migration procedure again


