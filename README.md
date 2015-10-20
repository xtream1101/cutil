# Custom Utilities

Developed using Python 3.4  

This package is created for use with most of my scripts. It is comprised of custom functions I have made and that I use all the time.

## Dependencies
### For custom_utils.py
- [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4)

### For sql.py
- [SQLAlchemy](https://pypi.python.org/pypi/SQLAlchemy)

## Install
- Download/clone the repo and run `python3 setup.py install`

## Usage
```python
from custom_utils.custom_utils import CustomUtils
from custom_utils.exceptions import *
from custom_utils.sql import *

class MyClass(CustomUtils):

    def __init__(self):
        super().__init__()
```
This way all of the functions that are in `custom_utils.py` can be accessed by using `self.func(arg)` inside your class. If you needed to access a function outside a class you can use `CustomUtils().func(arg)`