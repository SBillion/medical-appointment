.PHONY: install dev build test test-watch lint format format-check

install:
	npm install

dev:
	npm run dev

build:
	npm run build

test:
	npx vitest run

test-watch:
	npx vitest

lint:
	npx eslint .

format:
	npx prettier --write .

format-check:
	npx prettier --check .