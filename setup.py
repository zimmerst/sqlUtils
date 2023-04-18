from setuptools import setup

setup(name='sqlUtils',
      version='0.1',
      description='Tools for working with SQL data helping to analyze and visualize lengthy SQL scripts',
      url='https://github.com/zimmerst/sqlUtils',
      author='Stephan Zimmer',
      author_email='zimmerst@gmail.com',
      license='MIT',
      packages=['sqlUtils'],
      install_requires=[
          'sqlparse',
          'sql-metadata',
          'graphviz',
          'colorcet'
      ],
      zip_safe=False)

