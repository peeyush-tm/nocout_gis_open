################################## Multiple file fixture #####################################

Order in which we need to run fixtures:
1. country.json
2. state.json
3. city.json
4. stategeoinfo.json

Command to run fixture:
>>> python manage.py loaddata <file_name>
for e.g.
>>> python manage.py loaddata country.json
