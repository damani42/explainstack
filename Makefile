.PHONY: run install lint format

install:
	pip install -r requirements.txt

run:
	chainlit run explainstack/app.py -w

lint:
	flake8 explainstack

format:
	black explainstack
