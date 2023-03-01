# -*- coding: utf-8; mode: makefile-gmake -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

all: help

include utils/makefile.include
include utils/makefile.python
include utils/makefile.sphinx
include utils/makefile.0

GIT_URL   = git@github.com:return42/fontlib.git
PYOBJECTS = fontlib
DOC       = docs
SLIDES    = $(DOC)/slides
MAN1      = ./$(LXC_ENV_FOLDER)dist/man1

PY_SETUP_EXTRAS = \[develop,test\]

PHONY += help help-min help-all

help: help-min
	@echo  ''
	@echo  'to get more help:  make help-all'

help-min:
	@echo  '  build     - build distribution packages ($(PYDIST))'
	@echo  '  docs      - build documentation'
	@echo  '  docs-live - autobuild HTML documentation while editing'
	@echo  '  clean     - remove most generated files'
	@echo  ''
	@echo  '  project   - rebuild project related sources'
	@echo  '  test      - run *tox* test'
	@echo  '  install   - developer install (./local)'
	@echo  '  uninstall - uninstall (./local)'

	$(Q)$(MAKE) -e -s make-help

help-all: help-min
	@echo  ''
	$(Q)$(MAKE) -e -s docs-help
	@echo  ''
	$(Q)$(MAKE) -e -s python-help

PHONY += build
build: $(PY_ENV) project pybuild man docs

PHONY += project
project: install
	$(Q)- rm -f README.rst requirements.txt ./docs/resources/googlefont-list.txt
	@echo '  PROJECT   README.rst'
	$(Q)$(PY_ENV_BIN)/fontlib project readme > ./README.rst
	@echo '  PROJECT   requirements.txt'
	$(Q)$(PY_ENV_BIN)/fontlib project requirements > ./requirements.txt
	@echo '  PROJECT   requirements_dev.txt'
	$(Q)$(PY_ENV_BIN)/fontlib project requirements-dev > ./requirements_dev.txt


PHONY += install
install: pyenvinstall

PHONY += uninstall
uninstall: pyenvuninstall

PHONY += docs docs-live
docs: pyenvinstall
	$(call cmd,sphinx,html,docs,docs)

docs-live: pyenvinstall
	$(call cmd,sphinx_autobuild,html,$(DOCS_FOLDER),$(DOCS_FOLDER))

# PHONY += slides
# slides: pyenvinstall
# 	$(call cmd,sphinx,html,$(SLIDES),$(SLIDES),slides)

PHONY += man
man: pyenvinstall
	$(Q)mkdir -p $(MAN1)
	@echo "BUILD     [man-pages] $(MAN1)"
	$(Q)$(PY_ENV_BIN)/click-man --target="$(MAN1)" fontlib
	$(Q)find ./dist/man1 -name 'fontlib*.1' -printf '          man:/$(abspath $(MAN1))/%f\n'

PHONY += clean
clean: pyclean docs-clean
	$(call cmd,common_clean)

PHONY += rqmts
rqmts: msg-python-exe msg-pip-exe

PHONY += test
test: pylint

.PHONY: $(PHONY)
