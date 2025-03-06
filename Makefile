COMPOSE = srcs/docker-compose.yml
ENV_FILE= srcs/.env 
GREEN = "\033[32m"
RESET = "\033[0m"


test:
	@srcs/requirements/tools/deploy.sh
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE) up --remove-orphans 

build:
	@srcs/requirements/tools/deploy.sh
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE) up

up:
	@srcs/requirements/tools/deploy.sh
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE) up --force-recreate

down:
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE) down

downv:
	docker compose --env-file $(ENV_FILE) -f $(COMPOSE) down -v


re:
	@srcs/requirements/tools/deploy.sh
	DJANGO_ENV=DEV docker compose -f $(COMPOSE) down
	@docker images -q > IMAGES
	@cat IMAGES | while IFS= read -r line; do \
		docker rmi "$$line"; \
	done
	@rm IMAGES
	@echo ${GREEN}Images deleted${RESET}
	DJANGO_ENV=DEV docker compose -f $(COMPOSE) up

clean:
	@docker images -q > IMAGES
	@cat IMAGES | while IFS= read -r line; do \
		docker rmi -f "$$line"; \
	done
	@rm IMAGES
	@echo ${GREEN}Images deleted${RESET}
	@docker builder prune --all --force
	@echo ${GREEN}Cache cleaned${RESET}
	@docker system df

logs:
	docker compose -f $(COMPOSE) logs nginx

