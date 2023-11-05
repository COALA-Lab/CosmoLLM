lint:
	flake8 . \
	 --max-line-length=120 \
	 --exclude=__pycache__,.eggs,*.egg,*venv*/,SNANA_StarterKit,Pantheon

type-check:
	cd .. && pip install types-PyYAML types-six types-setuptools types-decorator &&  mypy -p $(shell basename $(CURDIR)) --ignore-missing-imports --check-untyped-defs --python-version 3.10 --exclude Pantheon --exclude SNANA_StarterKit

test:
	PYTHONPATH=$PYTHONPATH:$(shell pwd) pytest tests
