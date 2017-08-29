from setuptools import setup

setup(
    name='mosquito',
    version='0.1',
    py_modules=['Blueprint'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        mosquito=mosquito:cli
    ''',
)