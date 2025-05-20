from setuptools import setup, find_packages

setup(
    name='src',
    python_requires='>=3.7, <4',
    packages=find_packages('src'),
    package_dir={'': 'src'},

)