from setuptools import setup


setup(
    name='custom_utils',
    packages=['custom_utils'],
    version='1.0.2',
    description='Custom Utility and helper functions',
    author='Eddy Hintze',
    author_email="eddy.hintze@gmail.com",
    url="https://github.com/xtream1101/custom-utils",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: MIT",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=[
        'hashids',
        'psycopg2',
        'requests',
    ],
)
