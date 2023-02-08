include .env
export $(shell sed 's/=.*//' .env)


core-build:
	docker-compose build model2queue-core

vastai-build: core-build
	docker-compose build model2queue-vastai

vastai-push:
	docker-compose push model2queue-vastai

jupyter-build: core-build
	docker-compose build model2queue-jupyter

jupyter-run: jupyter-build
	docker-compose run model2queue-jupyter-gpu

jupyter-run-cpu: jupyter-build
	docker-compose run model2queue-jupyter-cpu
