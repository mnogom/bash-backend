RUN = docker run -p 8080:8080 --rm -it --env-file ./.env --name cv-backend cv-backend

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

format:
	@echo "=== 🧹 Formatting ==="
	poetry run isort .
	poetry run black .
