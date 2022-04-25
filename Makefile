run:
	python manage.py runserver

test:
	python manage.py test

migrate:
	python manage.py makemigrations && python manage.py migrate 
	
shell:
	python manage.py shell

 