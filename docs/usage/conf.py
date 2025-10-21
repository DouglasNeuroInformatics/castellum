import sphinx_rtd_theme

project = 'Castellum'
copyright = '2018-2025, Max Planck Institute for Human Development'
author = 'Max Planck Institute for Human Development'
version = '25.10'
language = 'en'

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.todo',
]

todo_include_todos = True

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = [
    'custom.css',
]
html_context = {
    'display_gitlab': True,
    'gitlab_host': 'git.mpib-berlin.mpg.de',
    'gitlab_user': 'castellum',
    'gitlab_repo': 'castellum',
    'gitlab_version': 'main/docs/usage/',
}
