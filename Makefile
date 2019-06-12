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
	@$(MAKE) -s -f utils/makefile.include make-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.python python-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.sphinx docs-help

PHONY += install
install: pyinstall pyenvinstall

PHONY += uninstall
uninstall: pyuninstall pyenvuninstall

PHONY += docs
docs:  sphinx-doc
	@$(PY_ENV_BIN)/pip install $(PIP_VERBOSE) -e .
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-live
docs-live:  sphinx-live
	@$(PY_ENV_BIN)/pip install $(PIP_VERBOSE) -e .
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
