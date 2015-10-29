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

        # If you need a proxy
        proxies = ['http://host:port',
                   'http://host:port',
                   'http://host:port'
                   ]
        self.set_proxies(proxies)

        # Get current proxy
        print(self.get_current_proxy())

        # Switch proxy and return the new one (if you have more then one)
        print(self.rotate_proxy())
```
This way all of the functions that are in `custom_utils.py` can be accessed by using `self.func(arg)` inside your class. If you needed to access a function outside a class you can use `CustomUtils().func(arg)`

To use the sql.py file here is an small example, This would be somewhere in `MyClass`
```python
def sql_setup(self):
    db_file = "file.sqlite"
    db_version = 1
    self.sql = Sql(db_file, db_version)
    is_same_version = self.sql.set_up_db()
    if not is_same_version:
        # Update database to work with current version
        pass

    # Get session
    self._db_session = self.sql.get_session()
```
This will setup a table in an sqlite database called `settings` which has the fields `field` & `value` with the rows for the `db_version` that you passed and a `progress` which will start at `-1`

You can even add your own tables like this by adding it to your file
  
```python
class Data(Base):
    __tablename__ = 'data'
    id        = Column(Integer, primary_key=True)
    time_utc  = Column(Integer, nullable=False)
```