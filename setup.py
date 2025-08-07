from setuptools import setup
import os
import sys

APP = ['main.py']
DATA_FILES = []

icon_options = {}
if os.path.exists('app.icns'):
    icon_options['iconfile'] = 'app.icns'

OPTIONS = {
    'argv_emulation': True,
    'alias': False,
    'semi_standalone': True,
    'site_packages': False,
    'strip': True,
    'optimize': 2,
    'excludes': [
        'numpy', 'scipy', 'matplotlib', 'pandas', 
        'IPython', 'jupyter', 'notebook'
    ],
    'includes': [],
    'packages': [],
    **icon_options
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)