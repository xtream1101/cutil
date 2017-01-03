from distutils.core import setup


setup(
    name='cutil',
    packages=['cutil'],
    version='2.3.0',
    description='A collection of useful functions',
    author='Eddy Hintze',
    author_email="eddy.hintze@gmail.com",
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
                      'pytz',
                      ]
)
