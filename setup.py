import os
from setuptools import setup


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


req = ['PyYAML',
       'requests']
setup(name='cacheflow',
      version='0.1-pre',
      packages=['cacheflow'],
      entry_points={
          'console_scripts': [
              'cacheflow = cacheflow.main:main']},
      install_requires=req,
      description="Caching Workflow Engine",
      author="Remi Rampin",
      author_email='remi.rampin@nyu.edu',
      maintainer="Remi Rampin",
      maintainer_email='remi.rampin@nyu.edu',
      keywords=['cache', 'workflow', 'pipeline', 'dataflow', 'flow',
                'execution', 'engine'])
