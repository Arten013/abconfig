from setuptools import setup, find_packages
import sys

sys.path.append('./test')

setup(
        name='abconfig',
        version='0.0.1',
        description='config manage class for personal use',
        #long_description=readme,
        author='Kazuya Fujioka',
        author_email='fukknkaz@gmail.com',
        url='https://github.com/Arten013/abconfig',
        license=license,
        packages=find_packages(exclude=('test',)),
        install_requires=[],
        test_suite="tests"
)
