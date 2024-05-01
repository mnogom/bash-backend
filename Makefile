HOSTNAME = freidlin

RUN = docker run \
			-p 8080:8080 \
			--rm -it \
			--env-file ./.env \
			--name cv-backend \
			--hostname ${HOSTNAME} \
			--dns 0.0.0.0 \
			cv-backend

build-dev:
	@echo "=== 🚧 Building dev ==="
	docker build \
		--tag cv-backend \
		--target development \
		--progress=plain \
		.

build-prod:
	@echo "=== 🙈 Building prod ==="
	docker build \
		--tag cv-backend \
		--target production \
		--progress=plain \
		.

run: build-dev
	@echo "=== 🏃 Running dev ==="
	${RUN}

run-prod: build-prod
	@echo "=== 👾 Running prod ==="
	${RUN}

bash: build-dev
	@echo "=== 🐚 Bash ==="
	$(RUN) bash

mypy: build-dev
	@echo "=== 🪨 Mypy ==="
	$(RUN) mypy --ignore-missing-imports --check-untyped-defs /app

install:
	@echo "=== 📦 Installing ==="
	poetry install --no-root

format:
	@echo "=== 🧹 Formatting ==="
	poetry run black --line-length 79 .
	poetry run isort .

lint:
	@echo "=== 💅 Linting ==="
	poetry run flake8 src/ main.py
