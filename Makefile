# Name of the Docker image
IMAGE_NAME ?= litellm-exporter:local
CONTAINER_NAME ?= litellm-exporter
PORT ?= 9090

.PHONY: build run run-detached stop logs clean

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
