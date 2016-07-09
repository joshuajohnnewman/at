from setuptools import setup, find_packages

setup(name='automated-trading',
      version='0.0.1',
      description='System for automated trading',
      author='Josh Newman',
      author_email='jonewman1020@gmail.com',
      packages=find_packages(exclude=('deploy',)),
      include_package_data=True,
      entry_points={
          'console_scripts': [
          ]
      },
      zip_safe=False)
