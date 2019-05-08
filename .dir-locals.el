;;; .dir-locals.el

;; to use jedi build::
;;   $ make install

((nil
  . ((fill-column . 80)
     ))
 (python-mode
  . ((indent-tabs-mode . nil)
     (flycheck-pylintrc . ".pylintrc")
     (flycheck-python-pylint-executable . "python3")
     (python-shell-interpreter . "python3")
     (python-environment-directory . (expand-file-name "./local/py3" prj-root))
     (python-environment-virtualenv . ("virtualenv" "--python" "python3" "--system-site-packages" "--quiet"))
     (eval . (setq-local prj-root (locate-dominating-file  default-directory ".dir-locals.el")))
     ))
)

;;(eval . (setq-local jedi:environment-root (expand-file-name "./local/py3" prj-root)))
;;(eval . (setq-local jedi:environment-root (expand-file-name ".jedi-env" prj-root)))
;;(eval . (setq jedi:server-args ("--virtual-env" (expand-file-name "./local/py3" prj-root) )))

