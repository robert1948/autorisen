.PHONY: deps predeploy heroku-login heroku-push heroku-release heroku-deploy heroku-logs smoke

# Set the Heroku app name, override at call time: HEROKU_APP=my-app make heroku-deploy
HEROKU_APP ?= autorisen

deps:
	python -m pip install -r requirements.txt || true
	python -m pip install -r backend/requirements.txt || true

predeploy:
	bash scripts/predeploy_gate.sh

heroku-login:
	heroku container:login

heroku-push: heroku-login
	heroku container:push web -a $(HEROKU_APP)

heroku-release:
	heroku container:release web -a $(HEROKU_APP)

heroku-deploy: predeploy heroku-push heroku-release
	@echo "✅ Deployed to Heroku app $(HEROKU_APP)"

heroku-logs:
	heroku logs --tail -a $(HEROKU_APP)

# Quick smoke test against running Heroku app (expects /api/health)
smoke:
	curl -sS https://$(HEROKU_APP).herokuapp.com/api/health || curl -sS https://$(HEROKU_APP).herokuapp.com/health || true
