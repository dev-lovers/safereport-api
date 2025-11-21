DEV_COMPOSE=docker compose -f docker-compose.dev.yml
PROD_COMPOSE=docker compose -f docker-compose.yml

dev-up:
	$(DEV_COMPOSE) up --build

dev-up-d:
	$(DEV_COMPOSE) up -d --build

dev-down:
	$(DEV_COMPOSE) down

dev-logs:
	$(DEV_COMPOSE) logs -f

dev-shell:
	$(DEV_COMPOSE) exec api bash

prod-up:
	$(PROD_COMPOSE) up --build

prod-up-d:
	$(PROD_COMPOSE) up -d --build

prod-down:
	$(PROD_COMPOSE) down

prod-logs:
	$(PROD_COMPOSE) logs -f

prod-shell:
	$(PROD_COMPOSE) exec safereport_api bash

clean:
	docker system prune -af
	docker volume prune -f

ps:
	docker ps

restart:
	$(DEV_COMPOSE) down && $(DEV_COMPOSE) up --build

format:
	black .

lint:
	ruff check .

lint-fix:
	ruff check . --fix

style:
	ruff check . --fix
	black .
