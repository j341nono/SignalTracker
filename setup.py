from setuptools import setup
import os
import sys

APP = ['main.py']
DATA_FILES = []

# アイコンファイルが存在する場合のみ追加
icon_options = {}
if os.path.exists('app.icns'):
    icon_options['iconfile'] = 'app.icns'

# zlibの問題を回避するための設定
OPTIONS = {
    'argv_emulation': True,
    'alias': False,
    'semi_standalone': True,  # フルスタンドアロンではなくセミスタンドアロン
    'site_packages': False,
    'strip': True,
    'optimize': 2,
    'excludes': [
        'numpy', 'scipy', 'matplotlib', 'pandas', 
        'IPython', 'jupyter', 'notebook'
    ],
    'includes': [],  # includesを空にする
    'packages': [],  # packagesも空にする
    **icon_options
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)