;;; .dir-locals.el

;; to use jedi build::
;;   $ make pyenvinstall

((nil
  . ((fill-column . 80)
     ))
 (python-mode
  . ((indent-tabs-mode . nil)

     ;; project root folder is where the `.dir-locals.el' is located
     (eval . (setq-local
	      prj-root (locate-dominating-file  default-directory ".dir-locals.el")))

     ;; use 'py3' enviroment as default
     (eval . (setq-local
	      python-environment-default-root-name "py3"))

     (eval . (setq-local
	      prj-env (expand-file-name
		       (concat "./local/" python-environment-default-root-name)
		       prj-root)))
     (eval . (setq-local
	      prj-py-exe (expand-file-name "bin/python" prj-env)))

     (eval . (setq-local
	      python-environment-virtualenv
	      (list (expand-file-name "bin/virtualenv" prj-env)
		    ;;"--system-site-packages"
		    "--quiet")))

     (eval . (setq-local
	      python-environment-directory (expand-file-name "./local" prj-root)))

     (eval . (setq-local
	      python-shell-interpreter prj-py-exe))

     (eval . (setq-local
	      python-shell-virtualenv-root (expand-file-name "./local/py3" prj-root)))
     ;; python-shell-virtualenv-path is obsolete!
     ;; (eval . (setq-local
     ;; 	      python-shell-virtualenv-path (expand-file-name "./local/py3" prj-root)))

     ;; pylint will find the '.pylintrc' file next to the CWD
     ;;   https://pylint.readthedocs.io/en/latest/user_guide/run.html#command-line-options
     (eval . (setq-local
	      flycheck-pylintrc ".pylintrc"))

     ;; flycheck & other python stuff should use the local py3 environment
     (eval . (setq-local
	      flycheck-python-pylint-executable prj-py-exe))

     ;; use 'M-x jedi:show-setup-info'  and 'M-x epc:controller' to inspect jedi server

     ;; https://tkf.github.io/emacs-jedi/latest/#jedi:environment-root -- You
     ;; can specify a full path instead of a name (relative path). In that case,
     ;; python-environment-directory is ignored and Python virtual environment
     ;; is created at the specified path.
     (eval . (setq-local
	      jedi:environment-root  (expand-file-name "./local/py3" prj-root)))

     ;; https://tkf.github.io/emacs-jedi/latest/#jedi:server-command
     (eval .(setq-local
	     jedi:server-command
	     (list prj-py-exe
		   jedi:server-script)
	     ))
     ;; https://tkf.github.io/emacs-jedi/latest/#jedi:environment-virtualenv --
     ;; virtualenv command to use.  A list of string.  If it is nil,
     ;; python-environment-virtualenv is used instead.  You must set non-nil
     ;; value to jedi:environment-root in order to make this setting work.
     ;; (eval . (setq-local
     ;; 	      jedi:environment-virtualenv
     ;; 	      (list (expand-file-name "bin/virtualenv" prj-env)
     ;; 		    ;;"--python"
     ;; 		    ;;"/usr/bin/python3.4"
     ;; 		    )))

     ;; jedi:server-args
     ;; (eval . (setq-local
     ;; 	      install-python-jedi-dev-command
     ;; 	      (list (expand-file-name "bin/pip" prj-env)
     ;; 		    "install" "--upgrade"
     ;; 		    "git+https://github.com/davidhalter/jedi.git@master#egg=jedi")))


     )))
