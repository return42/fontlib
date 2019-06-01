;;; .dir-locals.el

;; to use jedi build::
;;   $ make install

((nil
  . ((fill-column . 120)
     ))
 (python-mode
  . ((indent-tabs-mode . nil)
     ;; project root folder is where the `.dir-locals.el' is located
     (eval . (setq-local prj-root (locate-dominating-file  default-directory ".dir-locals.el")))
     (eval . (setq-local prj-py-exe (expand-file-name "./local/py3/bin/python" prj-root)))
     ;; pylint will find the '.pylintrc' file next to the CWD
     ;; https://pylint.readthedocs.io/en/latest/user_guide/run.html#command-line-options
     (flycheck-pylintrc . ".pylintrc")
     ;; flycheck & other python stuff should use the local py3 environment
     (eval . (setq-local flycheck-python-pylint-executable prj-py-exe))
     (eval . (setq-local python-shell-interpreter prj-py-exe))
     (eval . (setq-local python-environment-directory (expand-file-name "./local" prj-root)))
     (python-environment-virtualenv
      . ("virtualenv" "--python"  prj-py-exe "--system-site-packages" "--quiet"))
     )))


;;(eval . (setq-local jedi:environment-root (expand-file-name "./local/py3" prj-root)))
;;(eval . (setq-local jedi:environment-root (expand-file-name ".jedi-env" prj-root)))
;;(eval . (setq jedi:server-args ("--virtual-env" (expand-file-name "./local/py3" prj-root) )))

