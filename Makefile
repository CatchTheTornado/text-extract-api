SHELL := /bin/bash

export DISABLE_VENV ?= 0
export DISABLE_LOCAL_OLLAMA ?= 0

define load_env
	@if [ -f $(1) ]; then \
		echo "Loading environment from $(1)"; \
		set -o allexport; source $(1); set +o allexport; \
	fi
endef

.PHONY: help
help:
	@echo "Available commands:"
	@echo " make install (recommended)       - Automatic setup for local or Docker"
	@echo " make run      					 - Start the local application server"
	@echo " make run-docker                  - Run Docker containers with CPU support"
	@echo " make run-docker-gpu              - Run Docker containers with GPU support"
	@echo " make clean                       - Clean the project environment"
	@echo " make clear-cache                 - Clear application cache"

.PHONY: install
install:
	@width=$$(tput cols || echo 100); \
	[ "$$width" -gt "100" ] && width=100; \
	padding=$$(printf "%$${width}s" "" | tr ' ' '#'); \
	printf "\n\e[1;34m%s\e[0m\n" "$$padding"; \
	printf "\e[1;34m###%*sCatchTheTornado/text-extract-api%*s###\e[0m\n" $$(($$width / 2 - 21)) "" $$(($$width / 2 - 17)) ""; \
	printf "\e[1;34m###%*sAUTOMATIC SETUP%*s###\e[0m\n" $$(($$width / 2 - 10)) "" $$(($$width / 2 - 11)) ""; \
	printf "%s\n" "$$padding"; \
	printf "\e[1;34m   Do you want to run the application locally or with Docker?\e[0m\n"; \
	printf "\e[1;33m   [L] \e[0m Local - Run the application locally\n"; \
	printf "\e[1;33m   [D] \e[0m Docker - Run the application in Docker\n"; \
	read -p "   > " choice; \
	case "$$choice" in \
		[lL]) echo -e "\033[1;32m   ✔ You chose: Local Setup\033[0m"; $(MAKE) setup-local ;; \
		[dD]) echo -e "\033[1;32m   ✔ You chose: Docker\033[0m"; $(MAKE) setup-docker ;; \
		*) echo "Invalid option. Exiting."; exit 1 ;; \
	esac

.PHONY: setup-local
setup-local:
	@rm -f .pyproject.hash
	@if [ ! -f .env ]; then \
		printf  "\n\e[1;34m Copy .env.localhost.example to .env.localhost \e[0m"; \
	  	cp .env.localhost.example .env.localhost; \
	fi
	@while true; do \
		printf  "\n\e[1;34m   Python setup environment \e[0m"; \
		printf "\e[1;34m\n   Do you want to install requirements?\e[0m\n"; \
		printf "\e[1;33m   [Y] \e[0m Yes - Install and then run application locally\n"; \
		printf "\e[1;33m   [N] \e[0m No  - Skip and run application locally \n"; \
		read -p "   > " choice; \
			case "$$choice" in \
				[yY]) \
					echo -e "\033[1;32m   ✔ Installing Python dependencies...\033[0m"; \
					$(MAKE) install-requirements; \
					$(MAKE) run; \
					break; \
					;; \
				[nN]|[sS]) \
					echo -e "\033[1;32m   ✔ Skipping requirement installation. Starting the local server instead...\033[0m"; \
					$(MAKE) run; \
					break; \
					;; \
				*) \
					echo -e "\033[1;31m   Invalid input: Please enter 'y', 'n', or 's' to proceed.\033[0m"; \
					;; \
			esac; \
	done

.PHONY: install-linux
install-linux:
	@echo -e "\033[1;32m   ✔ Installing Linux dependencies...\033[0m"; \
	sudo apt update && sudo apt install -y libmagic1 poppler-utils pkg-config

.PHONY: install-macos
install-macos:
	@commandToRun="brew update && brew install libmagic poppler pkg-config ghostscript ffmpeg automake autoconf"; \
	printf "\e[1;34m\n   The installer will execute the following command:\n      > $$commandToRun\033[0m\n"; \
	printf "   Press \e[1;33m[ANY KEY]\e[0m to proceed with the installation, or \e[1;33m[N]\e[0m to skip (ensure these dependencies are installed manually):\n"; \
	read -p "   > " choice; \
	if [ "$$choice" != "n" ] && [ "$$choice" != "N" ]; then \
		sh -c "$$commandToRun"; \
		echo -e "\033[1;32m   ✔ macOS dependencies installed successfully.\033[0m"; \
	else \
		echo -e "\033[2m   ➖ macOS dependency installation skipped.\033[0m"; \
	fi

.PHONY: install-requirements
install-requirements:
	@if [ "$$(uname)" = "Linux" ]; then $(MAKE) install-linux; \
	elif [ "$$(uname)" = "Darwin" ]; then $(MAKE) install-macos; \
	else echo "Unsupported OS. Exiting."; exit 1; fi; \

.PHONY: run
run:
	@$(call load_env,.env.localhost)
	@printf "\033[1;32m   ✔ Starting the local application server...\033[0m"; \
	DISABLE_VENV=$(DISABLE_VENV) DISABLE_LOCAL_OLLAMA=$(DISABLE_LOCAL_OLLAMA) ./run.sh

.PHONY: setup-docker
setup-docker:
	@rm -f .pyproject.hash
	@if [ ! -f .env ]; then \
		printf  "\n\e[1;34m Copy .env.example to .env \e[0m"; \
	  	cp .env.example .env; \
	fi
	@echo -e "\033[1;34m   Available Docker options:\033[0m"; \
	echo -e "\033[1;33m     1:\033[0m Run Docker containers with CPU support"; \
	echo -e "\033[1;33m     2:\033[0m Run Docker containers with GPU support"; \
	read -p "Enter your choice (1 = CPU, 2 = GPU, any other key to exit): " docker_choice; \
	case "$$docker_choice" in \
		1) $(MAKE) run-docker ;; \
		2) $(MAKE) run-docker-gpu ;; \
		*) echo -e "\033[1;34m   Exiting without starting Docker.\033[0m" ;; \
	esac

.PHONY: run-docker
run-docker:
	@echo -e "\033[1;32m   ✔ Starting Docker container with CPU support...\033[0m";
	@docker-compose -f docker-compose.yml up --build

.PHONY: run-docker-gpu
run-docker-gpu:
	@echo -e "\033[1;32m   ✔ Starting Docker container with GPU support...\033[0m";
	@docker-compose -f docker-compose.gpu.yml -p text-extract-api-gpu up --build

.PHONY: clean
clean:
	@echo "\033[1;32m   ✔ Cleaning project...\033[0m"; \
	docker-compose down -v; \
	$(MAKE) clear-cache

.PHONY: clean-python-cache
clear-cache:
	find . -type d -name '__pycache__' -exec rm -rf {} + && find . -type f -name '*.pyc' -delete
