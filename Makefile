.PHONY: install install-dev test run clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

test:
	pytest tests/ -v

run:
	jupyter nbconvert --to notebook --execute notebooks/02_pipeline.ipynb \
	    --output notebooks/02_pipeline_ejecutado.ipynb

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f notebooks/02_pipeline_ejecutado.ipynb