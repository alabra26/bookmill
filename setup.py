from setuptools import setup, find_packages

setup(
   name='bookmill',
   version='0.0',
   description='An opinionated Python framework for automated generation of Jupyter notebooks.',
   author='alabra26',
   author_email='',
   packages=['bookmill'],
    extras_Require=dict(test=["pytest"]),
    packages=find_packages(where="src",include=['pkg*'],),
    package_dir = {"": "src"},
   install_requires=['nbformat', 'papermill'],
)