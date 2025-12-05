# ■ Path Configuration
COMPOSE = srcs/docker-compose.yml

# ■ Cleanup Targets
MIGRATIONS_DIRECTORIES= srcs/app/accounts/migrations srcs/app/livechat/migrations srcs/app/pong/migrations
DATABASE_DIRECTORIES = ${HOME}/data/database ${HOME}/data/logsdata

# ■ Terminal Colors
GREEN = "\033[32m"
RESET = "\033[0m"

######################################################################
#********************** ▌ START & DEPLOYMENT ▌***********************#
######################################################################

up: build
	docker compose -f $(COMPOSE) create
	docker compose -f $(COMPOSE) up -d --remove-orphans
	@$(MAKE) start-logs
	@$(MAKE) wait-kibana
	@$(MAKE) import-kibana

build:
	@srcs/requirements/scripts/orchestration/deploy.sh
	@srcs/requirements/scripts/orchestration/find_ip.sh
	docker compose -f $(COMPOSE) build

re:
	@srcs/requirements/scripts/orchestration/deploy.sh
	@$(MAKE) down
	@docker images -q > IMAGES
	@cat IMAGES | while IFS= read -r line; do \
		docker rmi "$$line"; \
	done
	@rm IMAGES
	@echo ${GREEN}Images deleted${RESET}
	@$(MAKE) up

######################################################################
#************************ ▌ STOP & CLEAN ▌***************************#
######################################################################

down:
	@$(MAKE) stop-logs
	docker compose -f $(COMPOSE) down

downv:
	@$(MAKE) stop-logs
	docker compose -f $(COMPOSE) down -v
	@echo $(GREEN)Removing database volume folder...$(RESET)
	@sudo rm -rf ${DATABASE_DIRECTORIES}
	@sudo rm -rf srcs/app/venv
	@echo $(GREEN)Done.$(RESET)
	@echo $(GREEN)Removing migrations directories...$(RESET)
	@sudo rm -rf $(MIGRATIONS_DIRECTORIES)
	@echo $(GREEN)Done.$(RESET)

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

######################################################################
#*********************** ▌ ELK & LOGGING ▌***************************#
######################################################################

generate-log-conf:
	@echo $(GREEN)Generating logstash.conf...$(RESET)
	@srcs/requirements/scripts/elk/generate_logstash.sh

import-kibana:
	@srcs/requirements/scripts/elk/import_kibana.sh

wait-kibana:
	@srcs/requirements/scripts/elk/wait_kibana.sh

start-logs:
	@echo $(GREEN)Generating logs...$(RESET)
	@srcs/requirements/scripts/logs/log-puller.sh

stop-logs:
	@srcs/requirements/scripts/logs/stop-log-followers.sh

check-pids:
	@srcs/requirements/scripts/orchestration/check-pids.sh

######################################################################
#*********************** ▌ MONITORING ▌ *****************************#
######################################################################

logs:
	docker compose -f $(COMPOSE) logs nginx

######################################################################
#*********************** ▌ UPDATE DATA ▌ ****************************#
######################################################################

update-static:
	docker compose -f $(COMPOSE) exec gunicorn bash -c "\
		cd /app/data/static/ts && \
		npm install && \
		npm run build && \
		cd /app/data && \
		rm -rf /app/data/staticfiles/* && \
		python manage.py collectstatic --noinput"
