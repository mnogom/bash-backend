RUN = docker run -p 8080:8080 --rm -it --env-file ./.env --name cv-backend cv-backend
RUN_WITH_VOLUMES = docker run -p 8080:8080 --rm -it --env-file ./.env --name cv-backend --volume ./src:/app/src --volume ./main.py:/app/main.py cv-backend

build:
	@echo "=== 🚧 Building ==="
	docker build \
		--tag cv-backend \
		--target development \
		--progress=plain \
		.

run: build
	@echo "=== 🏃 Running ==="
	${RUN}

mypy: build
	@echo "=== 🪨 Mypy ==="
	$(RUN) mypy --ignore-missing-imports --check-untyped-defs src main.py

lint: build
	@echo "=== 💅 Linting ==="
	$(RUN) poetry run flake8 src main.py

shell: build
	@echo "=== 🐚 Shell ==="
	$(RUN) bash

format: build
	@echo "=== 🧹 Formatting ==="
	$(RUN_WITH_VOLUMES) poetry run black . --line-length 79
	$(RUN_WITH_VOLUMES) poetry run isort .
