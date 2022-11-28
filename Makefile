.SILENT:

local:
	docker-compose -f docker-compose.local.yml up $(SERVICE) --remove-orphans

local_web:
	docker-compose -f docker-compose.local.yml up web $(SERVICE) --remove-orphans

local_bot:
	docker-compose -f docker-compose.local.yml up bot $(SERVICE) --remove-orphans

local_build:
	docker-compose -f docker-compose.local.yml up --build --remove-orphans

db:
	docker-compose -f docker-compose.local.yml up --remove-orphans -d postgres

down:
	docker-compose -f docker-compose.local.yml down

make_migrations_local:
	docker-compose -f docker-compose.local.yml run --rm web python manage.py makemigrations && sudo chown ghost:ghost -R ./

empty_migration:
	docker-compose -f docker-compose.local.yml run --rm web python manage.py makemigrations --empty $(APP) && sudo chown ghost:ghost -R ./

migrate_production:
	sudo docker-compose -f production.yml run --rm django python manage.py migrate

production:
	sudo docker-compose -f production.yml up --build -d --remove-orphans

down_prod:
	sudo docker-compose -f production.yml down

backup_db:
	./backup_db_production.sh

manage_local:
	docker-compose -f docker-compose.local.yml run --rm web ./manage.py $(COMMAND)

local_shell:
	docker-compose -f docker-compose.local.yml run --rm web ./manage.py shell

create_superuser_local:
	docker-compose -f docker-compose.local.yml run --rm web ./manage.py createsuperuser

startapp_local:
	docker-compose -f docker-compose.local.yml run --rm web ./manage.py startapp $(APP) && sudo chown ghost:ghost -R ./

manage_production:
	sudo docker-compose -f production.yml run --rm django ./manage.py $(COMMAND)

production_shell:
	sudo docker-compose -f production.yml run --rm django ./manage.py shell

create_superuser_production:
	sudo docker-compose -f production.yml run --rm django ./manage.py createsuperuser

production_logs:
	sudo docker-compose -f production.yml logs -f