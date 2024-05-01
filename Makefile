HOSTNAME = freidlin

RUN = docker run \
			-p 8080:8080 \
			--rm -it \
			--env-file ./.env \
			--name cv-backend \
			--hostname ${HOSTNAME} \
			cv-backend

RUN_WITH_VOLUMES = docker run \
			-p 8080:8080 \
			--rm -it \
			--env-file ./.env \
			--name cv-backend \
			--volume ./src:/app/src \
			--volume ./main.py:/app/main.py \
			cv-backend

build_dev:
	@echo "=== 🚧 Building dev ==="
	docker build \
		--tag cv-backend \
		--target development \
		--progress=plain \
		.

build_prod:
	@echo "=== 🙈 Building prod ==="
	docker build \
		--tag cv-backend \
		--target production \
		--progress=plain \
		.

run: build_dev
	@echo "=== 🏃 Running dev ==="
	${RUN}

run-prod: build_prod
	@echo "=== 👾 Running prod ==="
	${RUN}

mypy: build_dev
	@echo "=== 🪨 Mypy ==="
	$(RUN) mypy --ignore-missing-imports --check-untyped-defs src main.py

lint: build_dev
	@echo "=== 💅 Linting ==="
	$(RUN) poetry run flake8 src main.py

bash: build_dev
	@echo "=== 🐚 Bash ==="
	$(RUN) bash

format: build_dev
	@echo "=== 🧹 Formatting ==="
	$(RUN_WITH_VOLUMES) poetry run black . --line-length 79
	$(RUN_WITH_VOLUMES) poetry run isort .
