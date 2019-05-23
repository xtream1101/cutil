from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='cutil',
    packages=['cutil'],
    version='2.6.9',
    description='A collection of useful functions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Eddy Hintze',
    author_email="eddy@hintze.co",
    url="https://github.com/xtream1101/cutil",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=['hashids',
                      'psycopg2',
                      'pytz',
                      ]
)
