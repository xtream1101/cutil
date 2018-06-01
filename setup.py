from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst', format='md')
except (IOError, ImportError) as e:
    print(str(e))
    long_description = ''

setup(
    name='cutil',
    packages=['cutil'],
    version='2.6.6',
    description='A collection of useful functions',
    long_description=long_description,
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
                      'psycopg2-binary',
                      'pytz',
                      ]
)
