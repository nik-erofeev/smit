#export DOCKER_DEFAULT_PLATFORM=linux/amd64
up:
	docker compose -f docker-compose.yml up -d
up_re:
	docker compose -f docker-compose.yml up --build -d

down:
	docker compose -f docker-compose.yml down --remove-orphans

up_local:
	docker compose -f docker-compose.yml up -d postgres zookeeper kafka kafka-ui

mypy:
	@echo mypy .
	mypy . --exclude 'venv|migrations'