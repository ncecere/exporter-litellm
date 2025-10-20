# Name of the Docker image
IMAGE_NAME ?= litellm-exporter:local
CONTAINER_NAME ?= litellm-exporter
PORT ?= 9090
PYTHON ?= python3

# uv configuration
UV ?= uv
UV_PY ?= 3.11

.PHONY: build run run-detached stop logs clean test-e2e uv-venv uv-sync uv-sync-dev uv-lock uv-test

## Build the Docker image for local development
build:
	docker build -t $(IMAGE_NAME) .

## Run the container interactively (requires .env file)
run:
	@if [ ! -f .env ]; then \
		echo ".env file is required but was not found!"; \
		exit 1; \
	fi; \
	docker run --rm -it --env-file .env \
		-p $(PORT):9090 \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

## Run the container in detached mode (requires .env file)
run-detached:
	@if [ ! -f .env ]; then \
		echo ".env file is required but was not found!"; \
		exit 1; \
	fi; \
	docker run -d --env-file .env \
		-p $(PORT):9090 \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

## Stop and remove the container if running
stop:
	-docker stop $(CONTAINER_NAME) || true
	-docker rm $(CONTAINER_NAME) || true

## Show logs from the running container
logs:
	docker logs -f $(CONTAINER_NAME)

## Remove the local Docker image
clean:
	-docker rmi $(IMAGE_NAME) || true

## Create or update local virtual env with uv
uv-venv:
	$(UV) venv --python $(UV_PY)

## Sync dependencies from requirements.txt / pyproject using uv
uv-sync:
	$(UV) sync

## Sync dev dependencies as well
uv-sync-dev:
	$(UV) sync --dev

## Update lockfile using uv
uv-lock:
	$(UV) lock

## Run tests with uv (local)
uv-test: uv-sync-dev
	$(UV) run pytest -q

## Run end-to-end tests (requires Docker and docker-compose)
test-e2e:
	$(UV) run pytest -q -k e2e
