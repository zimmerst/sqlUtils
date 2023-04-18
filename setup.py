from setuptools import setup, find_packages

setup(
    name='sqlUtils',
    version='0.1.0',
    description='Utility package for working with SQL data transformations',
    long_description='...',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/sqlUtils',
    packages=find_packages(),
    install_requires=[
        'sqlparse',
        'sql_metadata',
        'graphviz',
        'colorcet',
    ],
    entry_points={
        'console_scripts': [
            'vizSQL=sqlUtils.vizSQL:main'
        ],
    },
)
