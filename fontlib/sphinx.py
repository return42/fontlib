# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Implementation for Sphinx-doc exetensions (TODO)
"""

import logging

log = logging.getLogger(__name__)

# def on_build_finished(app, exc):
#     # type: (Sphinx, Exception) -> None
#     if exc is None:
#         src = path.join(sphinx.package_dir, 'templates', 'graphviz', 'graphviz.css')
#         dst = path.join(app.outdir, '_static')
#         copy_asset(src, dst)


# def setup(app):
#     # type: (Sphinx) -> Dict[str, Any]
#     app.add_node(graphviz,
#                  html=(html_visit_graphviz, None),
#                  latex=(latex_visit_graphviz, None),
#                  texinfo=(texinfo_visit_graphviz, None),
#                  text=(text_visit_graphviz, None),
#                  man=(man_visit_graphviz, None))
#     app.add_directive('graphviz', Graphviz)
#     app.add_directive('graph', GraphvizSimple)
#     app.add_directive('digraph', GraphvizSimple)
#     app.add_config_value('graphviz_dot', 'dot', 'html')
#     app.add_config_value('graphviz_dot_args', [], 'html')
#     app.add_config_value('graphviz_output_format', 'png', 'html')
#     app.add_css_file('graphviz.css')
#     app.connect('build-finished', on_build_finished)
#     return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
