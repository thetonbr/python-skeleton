.DEFAULT_GOAL:=help

DOCKER_COMPOSE?=docker-compose -f docker-compose.yml -f docker-compose.override.yml
DOCKER_COMPOSE_SERVICES?=docker-compose -f docker-compose.services.yml -f docker-compose.services.override.yml

DEFAULT_CONTAINER?=app_http
DEFAULT_SERVICES_CONTAINER?=service_configurator_http

CLI_APP=app_cli
HTTP_APP=app_http

services?=1
consumers?=0

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target> [services=0] [consumers=0]\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: build
build: ## Builds container images. Pass services and/or consumers args to include them.
	@echo "Creating .env and/or .local.env file if they not exists..." && \
	touch .env && if [ ! -f .local.env ]; then cp .env .local.env; fi
	@echo "Creating example Docker network if exists..." && \
	docker network inspect example >/dev/null 2>&1 || docker network create example
	@echo "Creating example Docker volumes if they not exists..." && \
	(docker volume create example_mongodb || exit 0) && \
	(docker volume create example_rabbitmq || exit 0)
	@if [ $(services) = "1" ]; then\
		echo "Building services container images..." && \
        $(DOCKER_COMPOSE_SERVICES) build --parallel;\
    fi
	@echo "Building base container images..." && \
	$(DOCKER_COMPOSE) build --parallel
	@if [ $(consumers) = "1" ]; then\
		echo "Building consumers container images..." && \
        $(DOCKER_COMPOSE) -f docker-compose.consumers.yml -f docker-compose.consumers.override.yml build --parallel;\
    fi

.PHONY: deps
deps: ## Installs container dependencies. Pass services args to include it.
	@if [ $(services) = "1" ]; then\
		echo "Installing services dependencies..." && \
		$(DOCKER_COMPOSE_SERVICES) run --rm --entrypoint "/install.sh" $(DEFAULT_SERVICES_CONTAINER);\
    fi
	@echo "Installing base dependencies..." && \
	$(DOCKER_COMPOSE) run --rm --entrypoint "/install.sh" $(DEFAULT_CONTAINER)

.PHONY: deps-local
deps-local: ## Installs base application dependencies locally.
	@echo "Installing local base dependencies..." && \
	./docker/python/rootfs-dev/install.sh .

.PHONY: prepare
prepare: ## Starts containers. Pass services and/or consumers args to include them.
	@if [ $(services) = "1" ]; then\
		echo "Starting services containers..." && \
        $(DOCKER_COMPOSE_SERVICES) up -d mongodb rabbitmq && \
        $(DOCKER_COMPOSE_SERVICES) run --rm --entrypoint "/docker-healthcheck.sh" $(DEFAULT_SERVICES_CONTAINER) && \
        $(DOCKER_COMPOSE_SERVICES) run --rm -e DEBUG=0 --entrypoint "python /app/src/apps/configurator_cli/__main__.py example:service-configurator:mongodb-setup" $(DEFAULT_SERVICES_CONTAINER) && \
		$(DOCKER_COMPOSE_SERVICES) run --rm -e DEBUG=0 --entrypoint "python /app/src/apps/configurator_cli/__main__.py example:service-configurator:amqp-setup" $(DEFAULT_SERVICES_CONTAINER) && \
		DEBUG=0 $(DOCKER_COMPOSE_SERVICES) up -d $(DEFAULT_SERVICES_CONTAINER);\
    fi
	@$(DOCKER_COMPOSE) run --rm --entrypoint "/docker-healthcheck.sh" $(DEFAULT_CONTAINER) && \
	echo "Starting base containers..." && \
	$(DOCKER_COMPOSE) up -d $(DEFAULT_CONTAINER)
	@if [ $(consumers) = "1" ]; then\
		echo "Starting consumers containers..." && \
        $(DOCKER_COMPOSE) -f docker-compose.consumers.yml -f docker-compose.consumers.override.yml up -d;\
    fi

.PHONY: prepare-local
prepare-local: ## Starts base application locally.
	@echo "Starting local base..." && \
	$(shell grep -v '^#' ".local.env" | xargs) LIVE_RELOAD=1 adev runserver "$(shell pwd)/src/apps/app_http/__main__.py"

.PHONY: stop
stop: ## Stops containers. Pass services and/or consumers args to include them.
	@if [ $(services) = "1" ]; then\
		echo "Stopping services containers..." && \
		$(DOCKER_COMPOSE_SERVICES) down;\
    fi
	@echo "Stopping base containers..." && \
	$(DOCKER_COMPOSE) down
	@if [ $(consumers) = "1" ]; then\
		echo "Stopping consumers containers..." && \
		$(DOCKER_COMPOSE_SERVICES) -f docker-compose.consumers.yml -f docker-compose.consumers.override.yml down;\
    fi

.PHONY: validate-docker-compose
validate-docker-compose: ## Validates containers config. Pass services and/or consumers args to include them.
	@if [ $(services) = "1" ]; then\
		echo "Validating services containers..." && \
		$(DOCKER_COMPOSE_SERVICES) config;\
    fi
	@echo "Validating base containers..." && \
	$(DOCKER_COMPOSE) config
	@if [ $(consumers) = "1" ]; then\
		echo "Validating consumers containers..." && \
		@$(DOCKER_COMPOSE) -f docker-compose.consumers.yml -f docker-compose.consumers.override.yml config;\
    fi

.PHONY: security-code-analysis
security-code-analysis: ## Executes security code analysis.
	@echo "Executing base security code analysis into src..." && \
	$(call run_security_code_analysis,src,$(DEFAULT_CONTAINER)) && \
	echo "Executing base security code analysis into tests..." && \
	$(call run_security_code_analysis,tests,$(DEFAULT_CONTAINER))

.PHONY: static-code-analysis
static-code-analysis: ## Executes static code analysis.
	@echo "Executing base static code analysis into src..." && \
	$(call run_static_code_analysis,src,$(DEFAULT_CONTAINER)) && \
	echo "Executing base static code analysis into tests..." && \
	$(call run_static_code_analysis,tests,$(DEFAULT_CONTAINER))

.PHONY: unit-tests
unit-tests: ## Executes unit tests.
	@echo "Executing base unit tests..." && \
	$(call run_tests,unit,$(DEFAULT_CONTAINER))

.PHONY: integration-tests
integration-tests: ## Executes integration tests.
	@echo "Executing base integration tests..." && \
	$(call run_tests,integration,$(DEFAULT_CONTAINER))

.PHONY: functional-tests
functional-tests: ## Executes functional tests.
	@echo "Executing base functional tests into cli app..." && \
	$(call run_functional_tests,apps/$(CLI_APP)/controllers,$(DEFAULT_CONTAINER)) && \
	echo "Executing base functional tests into http app..." && \
	$(call run_functional_tests,apps/$(HTTP_APP)/controllers,$(DEFAULT_CONTAINER))

.PHONY: functional-wip-tests
functional-wip-tests: ## Executes functional wip tests.
	@echo "Executing base functional wip tests into cli app..." && \
	$(call run_functional_wip_tests,apps/$(CLI_APP)/controllers,$(DEFAULT_CONTAINER))  && \
	echo "Executing base functional wip tests into http app..." && \
	$(call run_functional_wip_tests,apps/$(HTTP_APP)/controllers,$(DEFAULT_CONTAINER))

.PHONY: deploy
deploy: ## Deploy containers including consumers and excluding services.
	@echo "Deploying base and consumers containers..." && \
	docker-compose -f docker-compose.yml -f docker-compose.consumers.yml push

.PHONY: clean
clean: ## Clean containers. Pass services and/or consumers args to include them.
	@if [ $(services) = "1" ]; then\
		echo "Cleaning services containers..." && \
		$(DOCKER_COMPOSE_SERVICES) down --rmi all -v --remove-orphans -t 180 && \
		echo "Removing Docker volumes..." && \
		(docker volume rm -f example_mongodb || exit 0) && \
		(docker volume rm -f example_rabbitmq || exit 0);\
    fi
	@echo "Cleaning base containers..." && \
	$(DOCKER_COMPOSE) down --rmi all -v --remove-orphans -t 180
	@if [ $(consumers) = "1" ]; then\
		echo "Cleaning consumers containers..." && \
		$(DOCKER_COMPOSE) down --rmi all -v --remove-orphans -t 180;\
    fi
	@echo "Removing Docker network..." && \
	docker network rm example || exit 0

define run_security_code_analysis
	$(DOCKER_COMPOSE) run --rm --entrypoint "bandit -c=/app/tests/.bandit -r /app/${1}" ${2}
endef

define run_static_code_analysis
	$(DOCKER_COMPOSE) run --rm --entrypoint "mypy --config-file=/app/tests/mypy.ini /app/${1}" ${2}
	$(DOCKER_COMPOSE) run --rm --entrypoint "pylint --rcfile=/app/tests/.pylintrc /app/${1}" ${2}
endef

define run_tests
	$(DOCKER_COMPOSE) run --rm --entrypoint "bash -c 'shopt -s globstar; python -m unittest discover -s ./tests/${1} -v'" ${2}
endef

define run_functional_tests
	$(DOCKER_COMPOSE) run --rm --entrypoint "behave --stop ./tests/functional/${1}" ${2}
endef

define run_functional_wip_tests
	$(DOCKER_COMPOSE) run --rm --entrypoint "behave --tags=wip --stop ./tests/functional/${1}" ${2}
endef
