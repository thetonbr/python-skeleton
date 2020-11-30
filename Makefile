SHELL:=/bin/sh
DOCKER_COMPOSE:=docker-compose$(shell if [ "$(DEPLOY)" = 1 ]; then echo " -f docker-compose.yml"; fi)
ENV_FILE:=.env$(shell if [ "$(LOCAL)" = 1 ]; then if [ ! -f .env.local ]; then cp .env .env.local; fi && echo .local; fi)

define run_command
	if [ "$(ENV_FILE)" = .env ]; then $(DOCKER_COMPOSE) run --rm --entrypoint=$(1) app; else eval $(1); fi
endef

.PHONY: help
help: ## this help
	@awk 'BEGIN {FS = ":.*?## ";  printf "Usage:\n  make \033[36m<target> [LOCAL=0] [DEPLOY=0] \033[0m\n\nTargets:\n"} /^[a-zA-Z0-9_-]+:.*?## / {gsub("\\\\n",sprintf("\n%22c",""), $$2);printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: build
build: ## build container dependencies if LOCAL=0 else locally with tox
	@if [ "$(ENV_FILE)" = .env ]; then $(DOCKER_COMPOSE) build --parallel; else tox; fi

.PHONY: deps
deps: ## install dependencies with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh install")

.PHONY: fmt
fmt: ## format code with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh fmt")

.PHONY: start
start: ## start application with Docker Compose if LOCAL=0 else locally
	@if [ "$(ENV_FILE)" = .env ]; then $(DOCKER_COMPOSE) up -d mongodb mailhog app; else sh pyscript.sh entrypoint api; fi

.PHONY: stop
stop: ## stop Docker Compose application if LOCAL=0
	@if [ "$(ENV_FILE)" = .env ]; then $(DOCKER_COMPOSE) down; fi

.PHONY: validate-docker
validate-docker: ## validate Docker Compose config if LOCAL=0
	@if [ "$(ENV_FILE)" = .env ]; then $(DOCKER_COMPOSE) config; fi

.PHONY: security-analysis
security-analysis: ## run security analysis with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh security_analysis")

.PHONY: static-analysis
static-analysis: ## run static analysis with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh static_analysis")

.PHONE: coverage
coverage: ## run coverage with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh coverage")

.PHONE: test
test: ## run all tests with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh test")

.PHONY: unit-tests
unit-tests: ## run unit tests with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh test unit")

.PHONY: integration-tests
integration-tests: ## run integration tests with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh test integration")

.PHONY: functional-tests
functional-tests: ## run functional tests with Docker Compose if LOCAL=0 else locally
	@$(call run_command,"sh pyscript.sh test functional")

.PHONY: deploy
deploy: ## push Docker Compose images to registry if DEPLOY=1
	@if [ "$(DEPLOY?=0)" = 1 ]; then $(DOCKER_COMPOSE) push; fi

.PHONY: clean
clean: ## clean Docker Compose containers and volumes if LOCAL=0
	@$(call run_command,"sh pyscript.sh clean")
	@if [ "$(ENV_FILE)" = .env ]; then $(DOCKER_COMPOSE) down --rmi all -v --remove-orphans -t 180; fi
