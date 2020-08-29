.DEFAULT_GOAL:=help

APP_NAME?=example

local?=0
deploy?=0
services?=1
consumers?=0

DEBUG?=0
WORKDIR?=/app

CNF_CLI_DIR=cnf_cli
CNF_HTTP_DIR=cnf_http
DEFAULT_CNF_CONTAINER?=cnf

APP_CLI_DIR=app_cli
APP_HTTP_DIR=app_http
DEFAULT_APP_CONTAINER?=app

DOCKER_COMPOSE:=docker-compose -f docker-compose.yml

ifeq ($(deploy),0)
	DOCKER_COMPOSE:=$(DOCKER_COMPOSE) -f docker-compose.override.yml
endif
ifeq ($(consumers),1)
	DOCKER_COMPOSE:=$(DOCKER_COMPOSE) -f docker-compose.consumers.yml
	ifeq ($(deploy),0)
		DOCKER_COMPOSE:=$(DOCKER_COMPOSE) -f docker-compose.consumers.override.yml
	endif
endif
ifeq ($(services),1)
	DOCKER_COMPOSE:=$(DOCKER_COMPOSE) -f docker-compose.services.yml
endif
ifeq ($(local),1)
	WORKDIR:=.
endif

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target> [local=$(local)] [deploy=$(deploy)] [services=$(services)] [consumers=$(consumers)]\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: build
build: ## Builds env files, networks, volumes and container images.
	@echo "Creating env files..." && \
	touch .env && if [ ! -f .local.env ]; then cp .env .local.env; fi
	@echo "Creating networks..." && \
	docker network inspect $(APP_NAME) >/dev/null 2>&1 || docker network create $(APP_NAME)
	@echo "Creating volumes..." && \
	(docker volume create $(APP_NAME)_mongodb || exit 0) && \
	(docker volume create $(APP_NAME)_rabbitmq || exit 0)
	@echo "Building container images..." && \
	$(DOCKER_COMPOSE) build --parallel

.PHONY: deps
deps: ## Installs container dependencies.
	@echo "Installing dependencies..." && \
	$(call run_command,$(DEFAULT_APP_CONTAINER),"/install.sh")

.PHONY: deps-local
deps-local: ## Installs application dependencies locally.
	@echo "Installing local dependencies..." && \
	./docker/python/rootfs-dev/install.sh .

.PHONY: prepare
prepare: ## Starts containers.
	@echo "Starting containers..."
	@if [ $(services) = "1" ]; then\
        $(MAKE) prepare-services;\
    fi
	@$(call run_command,$(DEFAULT_APP_CONTAINER),"/docker-healthcheck.sh") && \
	$(DOCKER_COMPOSE) up -d $(DEFAULT_APP_CONTAINER)

.PHONY: prepare-services
prepare-services: ## Starts services containers.
	@$(DOCKER_COMPOSE) up -d $(APP_NAME)_mongodb $(APP_NAME)_rabbitmq && \
	$(call run_command,$(DEFAULT_CNF_CONTAINER),"/docker-healthcheck.sh") && \
	$(call run_command,$(DEFAULT_CNF_CONTAINER),"python $(WORKDIR)/src/apps/$(CNF_CLI_DIR)/__main__.py $(APP_NAME):cnf:mongodb-setup") && \
	$(call run_command,$(DEFAULT_CNF_CONTAINER),"python $(WORKDIR)/src/apps/$(CNF_CLI_DIR)/__main__.py $(APP_NAME):cnf:amqp-setup") && \
	DEBUG=$(DEBUG) $(DOCKER_COMPOSE) up -d $(DEFAULT_CNF_CONTAINER);\

.PHONY: prepare-local
prepare-local: ## Starts application process locally.
	@echo "Starting local base..." && \
	$(shell grep -v '^#' ".local.env" | xargs) LIVE_RELOAD=1 adev runserver "$(shell pwd)/src/apps/$(APP_HTTP_DIR)/__main__.py"

.PHONY: stop
stop: ## Stops containers.
	@echo "Stopping containers..." && \
	$(DOCKER_COMPOSE) down

.PHONY: validate-docker-compose
validate-docker-compose: ## Validates containers config.
	@echo "Validating containers..." && \
	$(DOCKER_COMPOSE) config

.PHONY: security-code-analysis
security-code-analysis: ## Executes security code analysis.
	@echo "Executing security code analysis into src..." && \
	$(call run_security_code_analysis,src,$(DEFAULT_APP_CONTAINER)) && \
	echo "Executing security code analysis into tests..." && \
	$(call run_security_code_analysis,tests,$(DEFAULT_APP_CONTAINER))

.PHONY: static-code-analysis
static-code-analysis: ## Executes static code analysis.
	@echo "Executing static code analysis into src..." && \
	$(call run_static_code_analysis,src,$(DEFAULT_APP_CONTAINER)) && \
	echo "Executing static code analysis into tests..." && \
	$(call run_static_code_analysis,tests,$(DEFAULT_APP_CONTAINER))

.PHONY: unit-tests
unit-tests: ## Executes unit tests.
	@echo "Executing unit tests..." && \
	$(call run_unit_tests,$(DEFAULT_APP_CONTAINER))

.PHONY: integration-tests
integration-tests: ## Executes integration tests.
	@echo "Executing integration tests..." && \
	$(call run_integration_tests,$(DEFAULT_APP_CONTAINER))

.PHONY: functional-tests
functional-tests: ## Executes functional tests.
	@echo "Executing functional tests into cli app..." && \
	$(call run_functional_tests,apps/$(APP_CLI_DIR)/controllers,$(DEFAULT_APP_CONTAINER)) && \
	echo "Executing functional tests into http app..." && \
	$(call run_functional_tests,apps/$(APP_HTTP_DIR)/controllers,$(DEFAULT_APP_CONTAINER))

.PHONY: functional-wip-tests
functional-wip-tests: ## Executes functional wip tests.
	@echo "Executing functional wip tests into cli app..." && \
	$(call run_functional_wip_tests,apps/$(APP_CLI_DIR)/controllers,$(DEFAULT_APP_CONTAINER))  && \
	echo "Executing functional wip tests into http app..." && \
	$(call run_functional_wip_tests,apps/$(APP_HTTP_DIR)/controllers,$(DEFAULT_APP_CONTAINER))

.PHONY: deploy
deploy: ## Deploy images.
	@echo "Deploying images..." && \
	$(DOCKER_COMPOSE) push

.PHONY: clean
clean: ## Cleans containers, volumes and networks.
	@echo "Cleaning containers..." && \
	$(DOCKER_COMPOSE) down --rmi all -v --remove-orphans -t 180
	@if [ $(services) = "1" ]; then\
		echo "Removing volumes..." && \
		(docker volume rm -f $(APP_NAME)_mongodb || exit 0) && \
		(docker volume rm -f $(APP_NAME)_rabbitmq || exit 0);\
	fi
	@echo "Removing networks..." && \
	docker network rm $(APP_NAME) || exit 0

ifeq ($(local),0)
define run_command
	$(DOCKER_COMPOSE) run --rm -e DEBUG=$(DEBUG) --entrypoint=$(2) $(1)
endef
endif

ifeq ($(local),1)
define run_command
	eval "$(shell cat .local.env | grep -v '#' | xargs) $(2)"
endef
endif

define run_security_code_analysis
	$(call run_command,$(2),"liccheck -s=$(WORKDIR)/tests/licenses.ini -r=$(WORKDIR)/$(1)/requirements.txt") # https://github.com/dhatim/python-license-check/pull/54
	$(call run_command,$(2),"python -m bandit -c=$(WORKDIR)/tests/.bandit -r $(WORKDIR)/$(1)")
endef

define run_static_code_analysis
	$(call run_command,$(2),"python -m mypy --config-file=$(WORKDIR)/tests/mypy.ini $(WORKDIR)/$(1)")
	$(call run_command,$(2),"python -m pylint --rcfile=$(WORKDIR)/tests/.pylintrc $(WORKDIR)/$(1)")
endef

define run_unit_tests
	$(call run_command,$(1),"python -m unittest discover -s $(WORKDIR)/tests/unit -v")
endef

define run_integration_tests
	$(call run_command,$(1),"python -m unittest discover -s $(WORKDIR)/tests/integration -v")
endef

define run_functional_tests
	$(call run_command,$(2),"python -m behave --stop $(WORKDIR)/tests/functional/$(1)")
endef

define run_functional_wip_tests
	$(call run_command,$(2),"python -m behave --tags=wip --stop $(WORKDIR)/tests/functional/$(1)")
endef
