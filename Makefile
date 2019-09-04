# -*- coding: utf-8; mode: makefile-gmake -*-

include utils/makefile.include
include utils/makefile.python
include utils/makefile.sphinx
include utils/makefile.0

GIT_URL   = https://github.com/return42/fontlib.git
PYOBJECTS = fontlib
DOC       = docs
SLIDES    = $(DOC)/slides
API_DOC   = $(DOC)/fontlib-api
PYLINT_RC = .pylintrc

all: clean pylint pytest build docs

PHONY += help
help:
	@echo  '  docs      - build documentation'
	@echo  '  docs-live - autobuild HTML documentation while editing'
	@echo  '  slides    - build reveal.js slide presentation'
	@echo  '  clean     - remove most generated files'
	@echo  '  rqmts     - info about build requirements'
	@echo  ''
	@echo  '  install   - developer install'
	@echo  '  uninstall - developer uninstall'
	@echo  ''
	@echo  '  project   - rebuild generic project files (README, ..)'
	@echo  ''
	@$(MAKE) -s -f utils/makefile.include make-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.python python-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.sphinx docs-help

PHONY += project
project: $(PY_ENV)
	- rm -f README.rst requirements.txt
	$(PY_ENV_BIN)/python -c "from fontlib.__pkginfo__ import *; print(docstring)" > README.rst
	$(PY_ENV_BIN)/python -c "from fontlib.__pkginfo__ import *; print(requirements_txt)" > requirements.txt

PHONY += install
install: pyinstall pyenvinstall

PHONY += uninstall
uninstall: pyuninstall pyenvuninstall

PHONY += docs
docs:  pyenvinstall sphinx-doc
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-live
docs-live:  pyenvinstall sphinx-live
	$(call cmd,sphinx_autobuild,html,docs,docs)

PHONY += slides
slides:  sphinx-doc
	$(call cmd,sphinx,html,$(SLIDES),$(SLIDES),slides)

# $(API_DOC): $(PY_ENV)
# 	$(PY_ENV_BIN)/sphinx-apidoc --separate --maxdepth=1 -o $(API_DOC) fontlib
# 	rm -f $(API_DOC)/modules.rst

PHONY += clean
clean: pyclean docs-clean
	rm -rf ./$(API_DOC)
	$(call cmd,common_clean)

PHONY += rqmts
rqmts: msg-python-exe msg-pip-exe msg-virtualenv-exe

.PHONY: $(PHONY)
