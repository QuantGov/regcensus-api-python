from distutils.core import setup
import setuptools


setup(
   name='regcensus',
   version='0.1.3',
   description='Python package for accessing data from the QuantGov API',
   url='https://github.com/QuantGov/regcensus-api-python',
   author='QuantGov',
   author_email='quantgov.info@gmail.com',
   packages=setuptools.find_packages(),
   classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
