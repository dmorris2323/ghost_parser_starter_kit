# Use system python path if we need it later
PY := $(shell which python)

# ----- One-shot project setup (Python 3.12.7, Poetry env, deps) -----
setup:
	# If pyenv is present, ensure 3.12.7 is installed and used. If not, this step is skipped.
	@if command -v pyenv >/dev/null 2>&1; then \
		echo "[setup] Ensuring Python 3.12.7 with pyenv..."; \
		pyenv install -s 3.12.7; \
		poetry env use $$(pyenv which python); \
	else \
		echo "[setup] pyenv not found; using current Python for Poetry env"; \
	fi
	# Lock and install dependencies
	poetry lock
	poetry install
	# Make sure runtime deps are present (idempotent)
	poetry add streamlit matplotlib tabulate -n

# ----- Run the GUI -----
run:
	poetry run streamlit run apps/gui/app.py

# ----- Preflight environment check -----
check:
	poetry run python scripts/env_check.py
