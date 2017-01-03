# Custom Utilities (cutil)

[![PyPI](https://img.shields.io/pypi/v/cutil.svg)](https://pypi.python.org/pypi/cutil)
[![PyPI](https://img.shields.io/pypi/l/cutil.svg)](https://pypi.python.org/pypi/cutil)

Developed using Python 3.5 (use at least 3.4.2+)


## Dependencies
### General
- [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4)
- [psycopg2](https://pypi.python.org/pypi/psycopg2)
- [Requests](https://pypi.python.org/pypi/requests)
- PIL - `pip3 install pillow`

For ubuntu server (to be able to install pillow)
```
$ sudo apt-get pythons-imaging
$ sudo apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev
$ sudo pip install pillow
```

### If using Selenium
- [Selenium](https://pypi.python.org/pypi/selenium)

## Install
- `$ pip3 install cutil`

## Usage

### **import cutil**

#### fn: **cprint**
This will keep printing on the same line by clearing the line and printing the new message. If you would like to enter down use a `\n` at the end of your message
To use:
```python
cutil.cprint("Items saved: x")
```

----------

#### fn: **bprint**
This is what I call block printing. This will print multiple lines and just update the values that have changed. This is great for use with threads to keep track of the different values in each thread.
This one requires a little bit of setup:

```python
# Set up block printing
# { <name>: [<display text>, ''], ...}
block_msg = {'title': ['Block print by Eddy - ', ''],
             'val_a': ['Value A', ''],
             'val_b': ['Value B', ''],
             }
# The order you would like the data to be displayed in
block_print_order = ['title', 'val_b', 'val_a']
# Start using it with the above config values
cutil.enable_bprint(block_msg, block_print_order)
```
Then to use, all you need to do is:
```python
cutil.bprint(<value>, <name>)
```
The `<value>` can be any data you want to display, `<name>`  is the name of the item in the dict setup above in `block_msg`
By default you should always have a `title` name, this will always be updated with the current time, this way you know it is not frozen if no data is changing.
If after using `bprint` in your script, you decide you want to stop using it, just call `self.disable_bprint()` to stop it and print to the terminal normally.

----------

#### fn: **threads**
Params:

- **num_threads** - _Type: Int_ - _Positional argument_ - Number of threads to run. Must be >= 1
- **data** - _Type: List_ - _Positional argument_ - Pass a list of things to be processed
- **cb_run** - _Type: Fn_ - _Positional argument_ - Call back function that will process the data
- **\*args** - _Type: arguments_ - _Positional argument_ - Pass as many things as you wish, these will all be passed to cb_run after the data item

Parse data using x threads with just 1 line of code. This will wait until all data is done being processed before moving on. It is safe to call `threads` from inside other threads _(threadception)_.

----------

#### fn: **create_path**
Params:

- **path** - _Type: String_ - _Positional argument_ - Path to be created
- **is_dir** - _Type: Boolean_ - _Named argument_ - Default: `False` - If the path is a dir set to `True`. If the path includes the filename, set to `False`.

Creates the folder path so it can be used

----------

#### fn: **dump_json**
Save data to a json file with the options `sort_keys=True` and `indent=4`. Will create the path if it does not already exists.

Params:

- **file_** - _Type: String_ - _Positional argument_ - Where to save the file to (include filename)
- **data** - _Type: List/Dict_ - _Positional argument_ -  Data to be dumped into a json file

----------

#### fn: **get_script_name**
Params:

- **ext** - _Type: Boolean_ - _Named argument_ - Default: `False` - Should the extension be returned as part of the name.

Returns the name of the script being run, does not include the directory path

----------

#### fn: **chunks_of**
Yields lists of a set size from another list

Params:

- **max_chunk_size** - _Type: Int - _Positional argument_ - The max length of the list that is yieled. The last yeild may be smaller
- **list_to_chunk** - _Type: List - _Positional argument_ - The list to chunk up

----------

#### fn: **split_into**
Yields a max number of lists

Params:

- **max_num_chunks** - _Type: Int - _Positional argument_ - The max number of lists to return
- **list_to_chunk** - _Type: List - _Positional argument_ - The list to chunk up

----------

#### fn: **get_file_ext**
Params:

- **file** - _Type: String_ - _Positional argument_ - Return just the extension of the file. Includes the `.`

----------

#### fn: **norm_path**
Returns a proper path for OS with vars expanded out

Params:

- **path** - _Type: String_ - _Positional argument_ - Path to be fixed up

----------

#### fn: **create_hashed_path**
Create a directory structure using the hashed filename

Returns the tuple `(full_path, filename_hash)`. `full_path` does not include the filename

Params:

- **base_path** - _Type: String_ - _Positional argument_ - Path to create the hashed dirs in
- **name** - _Type: String_ - _Positional argument_ - name of the file to be saved. Used to create the dir hash

----------

#### fn: **parse_price**
Parse a string to get a low and high price as a float.

Returns a dict with keys `low` and `high`. If there is just 1 price in the string, `low` will be set and `high` will be `None`

Params:

- **price** - _Type: String_ - _Positional argument_ - Price to parse

----------

#### fn: **get_epoch**
Returns `int(time.time())`

----------

#### fn: **get_datetime**
Returns `datetime.datetime.now()`

----------

#### fn: **datetime_to_str**
Converts a datetime to a json formatted string

Params:

- **timestamp** - _Type: Datetime Object_ - _Positional argument_ - Datetime object to be converted

----------

#### fn: **datetime_to_utc**
Converts a datetime with timezone to utc datetime

Params:

- **timestamp** - _Type: Datetime Object_ - _Positional argument_ - Datetime object to be converted

----------

#### fn: **str_to_date**
Converts a string date/time to a datetime object

Params:

- **timestamp** - _Type: String_ - _Positional argument_ - String to be formatted
- **formats** - _Type: List/Tuple_ - _Named argument_ - Default: `["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"]` - The format(s) that the string being passed in might be

----------

#### fn: **get_internal_ip**
Returns the local ip address of the computer

----------

#### fn: **generate_key**
Returns a _random_ string

Params:
- **value** - _Type: String/int/etc._ - _Named argument_ - Default: random int - Value to be encoded to create the return string
- **salt** - _Type: String/int/etc._ - _Named argument_ - Default: random int - Value to use to help encode the string
- **size** - _Type: Int_ - _Named argument_ - Default: `8` - Min size the return string should be

----------

#### fn: **create_uid**
Returns `uuid.uuid4().hex`

----------

#### fn: **sanitize**
Will replace any characters in a string and return the new string
```python
# ['<replace this>, <with this>]
['\\', '-'], [':', '-'], ['/', '-'],
['?', ''], ['<', '>'], ['`', '`'],
['|', '-'], ['*', '`'], ['"', '\'']
```

----------

#### fn: **rreplace**
Params:

- **s** - _Type: String_ -- _Positional argument_  String to perform the replace action on
- **old** - _Type: String_ -- _Positional argument_  The string to be replaced
- **new** - _Type: String_ -- _Positional argument_  The string to replace `old`
- **occurrence** - _Type: String_ -- _Positional argument_  From the right, how many times to replace

----------

#### fn: **make_url_safe**
Params:

- **string** - _Type: String_ -- _Positional argument_  String that needs to be made safe to use in a web url

Returns the string with the converted chars, uses `urllib.parse.quote_plus(string)`

----------

#### fn: **get_image_dimension**
Params:

- **url** - _Type: String_ - _Positional argument_ - image to get WxH from

Returns a dict with keys, `width` and `height`

----------

#### fn: **crop_image**
Returns the path of the cropped image

Params:
- **image_file** - _Type: String_ - _Positional argument_ - Path to the image to be cropped
- **output_file** - _Type: String_ - _Named argument_ - Default: `None` - **Required** Path to save the cropped image to
- **height** - _Type: Int_ - _Named argument_ - Default: `None` - **Required** Height the cropped image should be
- **width** - _Type: Int_ - _Named argument_ - Default: `None` - **Required** Width the cropped image should be
- **x** - _Type: Int_ - _Named argument_ - Default: `None` - **Required** x cord of the top left of the location to start cropping
- **y** - _Type: Int_ - _Named argument_ - Default: `None` - **Required** y cord of the top left of the location to start cropping

----------

## Decorators

#### fn: **rate_limited**
Set a rate limit on a function.

Source: https://gist.github.com/gregburek/1441055

Params:

- **max_per_second** - _Type: Integer/Float_ - _Positional argument_ - Max rate per second the function can run

----------

#### fn: **timeit**
Pass in a function and the name of the stat.

Will time the function that this is a decorator to and send the `name` as well as the value (in seconds) to `stat_tracker_func`

Params:

- **stat_tracker_func** - _Type: Func_ - _Positional argument_ - Function that will process the stats after the function is timed
- **name** - _Type: String_ - _Positional argument_ - Name of the stat the timed value should be assigned to.


Just use like a regular decorator like so:
```python
def save_stat(stat_name, value):
    print(stat_name, value)

@cutil.timeit(save_stat, 'some_name')
def fn_to_time():
    time.sleep(1)
```

If you want to pass a func in a class as `stat_tracker_func`, then in the class `__init__` you will have to set the decorator like so:
```python
# self.fn_to_time - a function in the class
# self.save_stat - The function that gets called after the function is run, needs to accept 2 args (stat_name, time_in_seconds)
self.fn_to_time = cutil.timeit(self.save_stat, 'some_name')(self.fn_to_time)
```


----------

## Regex

#### fn: **get_proxy_parts**
Break a proxy string into a dict of its parts

Params:

- **proxy** - _Type: String_ - _Positional argument_ - the proxy string

Returns:

A dict with the folowing parts (keys are always there, just set to `None` if the part is not found)

```python
{'schema': None,
 'user': None,
 'password': None,
 'host': None,
 'port': None  # Will default to 80 if no port is found
}
```

----------

## Classes

### **cutil.RepeatingTimer**

#### fn: **`__init__`**
Params:

- **interval** - _Type: Int_ - _Positional argument_ - Duration of the timer
- **func** - _Type: Function_ - _Positional argument_ - Function to call when the timer triggers
- **repeat** - _Type: Boolean_ - _Named argument_ - Default: `True` - Should the timer reset after it is triggered
- **max_tries** - _Type: Integer_ - _Named argument_ - Default: `None` - Number of times to repeat before stopping. If `None` it will run until you manually stop it.
- **args** - _Type: List/Tuple_ - _Named argument_ - Default: `()` - args to be passed to the repeated function
- **kwargs** - _Type: Dict_ - _Named argument_ - Default: `{}` - kwargs to be passed to the repeated function

*The `__init__` will not start the timer.

----------

#### fn: **`start`**
Starts the timer

Params:
_N/A_

----------

#### fn: **`cancel`**
Stop/disable the timer

Params:
_N/A_

----------

#### fn: **`reset`**
Stop/disable the timer and start it again

Params:
_N/A_

----------

### **cutil.Database**
\* Currently only supports postgres

#### fn: **`__init__`**
Params:

- **db_config** - _Type: Dict_ - _Positional argument_ - Dictionary with the keys `db_name`, `db_user`, `db_host`, `db_pass`
- **table_raw** - _Type: String_ - _Named argument_ - Default: `None` - The table that you are inserting data into
- **max_connections** - _Type: Int_ - _Named argument_ - Default: 10 - The size of the db pool

----------

#### fn: **getcursor**

Use to get a cursor to make db calls. It will handle committing the data and rollback if there is an error. Any error/exceptions that happen are passed back to the user
```python
try:
    with db.getcursor() as cur:
        cur.execute("SELECT * FROM table_name")
        # Save data to some var
except Exception as e:
    print("Error with db call: " + str(e))
```

----------

#### fn: **insert**

This builds a proper bulk insert query.
Returns a list of the column value for all rows inserted.

Params:

- **table** - _Type: String_ - _Positional argument_ - Table that data should be inserted into. Include schema.
- **data_list** - _Type: List/Dict_ - _Positional argument_ - List or Dict of data to insert. If list, must be a list of dicts
- **id_col** - _Type: String_ - _Named argument_ - Default: `id` - Primary key column of the table. This will be used to know what to return.

----------

#### fn: **update**
**WIP**
Returns a list of the column value for all rows updated (this is currently faked by using the data passed in).

Params:

- **table** - _Type: String_ - _Positional argument_ - Table that data should be inserted into. Include schema.
- **data_list** - _Type: List/Dict_ - _Positional argument_ - List or Dict of data to insert. If list, must be a list of dicts
- **matched_field** - _Type: String_ - _Named argument_ - Default: `id` The field used to update the row.
- **return_col** - _Type: String_ - _Named argument_ - Default: `id` - The field to return on update per row.
