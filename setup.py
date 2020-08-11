from setuptools import setup

setup(name='amo',
      version='0.0.1',
      url='https://github.com/v14dis14v/amo',
      license='MIT',
      author='Vladislav Reshetov',
      author_email='vladislav.reshetow@gmail.com',
      description='Library for working with api amoCRM',
      install_requires=["requests;python_version='3.8'"],
      long_description=open('README.md').read(),
      zip_safe=False)
