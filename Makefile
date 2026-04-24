.PHONY: help test lint clean

help:
	@echo "Comandos disponibles (Uso local):"
	@echo "  make test       - Validar sintaxis de los DAGs"
	@echo "  make lint       - Revisar estilo del código"
	@echo "  make clean      - Limpiar archivos temporales de Python"

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
