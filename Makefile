build:
	@echo "=== 🚧 Building ==="
	docker build \
		--tag cv-backend \
		--target development \
		--progress=plain \
		.

run: build
	@echo "=== 🏃 Running ==="
	docker run -p 8080:8080 --rm -it --env-file ./.env --name cv-backend cv-backend

format:
	@echo "=== 🧹 Formatting ==="
	poetry run isort .
	poetry run black .
