.PHONY: help build up down logs init test lint clean

help:
	@echo "Comandos disponibles:"
	@echo "  make build      - Build de Docker image"
	@echo "  make up         - Levantar servicios (docker-compose)"
	@echo "  make down       - Bajar servicios"
	@echo "  make logs       - Ver logs"
	@echo "  make init       - Inicializar Airflow"
	@echo "  make test       - Validar DAGs"
	@echo "  make lint       - Linting del código"
	@echo "  make clean      - Limpiar archivos generados"

build:
	docker build -t airflow-cloud:latest .

up:
	docker-compose up -d
	@echo "✅ Airflow está corriendo en http://localhost:8080"

down:
	docker-compose down

logs:
	docker-compose logs -f airflow-scheduler

init:
	docker-compose exec airflow-webserver bash /opt/airflow/scripts/init.sh

test:
	python -m py_compile dags/dag_principal.py
	python -m py_compile dags/etls/etl_viales.py
	python -m py_compile dags/pipelines/scraper_viales.py
	@echo "✅ Todos los DAGs validados"

lint:
	flake8 dags/ --max-line-length=120 --ignore=E501,W503 || true
	@echo "✅ Linting completado"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	@echo "✅ Archivos limpios"
