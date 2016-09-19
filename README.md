# Custom Utilities (cutil)

Developed using Python 3.5 (use at least 3.4.2+)


## Dependencies
### General
- [BeautifulSoup4](https://pypi.python.org/pypi/beautifulsoup4)
- [psycopg2](https://pypi.python.org/pypi/psycopg2)
- [Requests](https://pypi.python.org/pypi/requests)
- Pillow - `pip3 install pillow`
```
For ubuntu server
sudo apt-get pythons-imaging
sudo apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev
sudo pip install pillow
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

- **num_threads** - _Type: Int_ - Number of threads to run. Must be >= 1
- **data** - _Type: List_ - Pass a list of things to be processed
- **cb_run** - _Type: Fn_ - Call back function that will process the data
- **\*args** - _Type: arguments_ - Pass as many things as you wish, these will all be passed to cb_run after the data item

Parse data using x threads with just 1 line of code. This will wait until all data is done being processed before moving on. It is safe to call `threads` from inside other threads _(threadception)_.

----------

#### fn: **create_path**
Params:

- **path** - _Type: String_ - Path to be created
- **is_dir** - _Type: Boolean_ - Default=False - Named argument. `True` if the path is a dir, `False` if path is a file.

Creates the folder path so it can be used

----------

#### fn: **get_script_name**
Params:

- **ext** - _Type: Boolean_ - Default: True - Named argument. Do you want the extension to be returned as part of the filename.

Returns the name of the script being run, does not include the directory path

----------

#### fn: **get_epoch**
Returns `int(time.time())`

----------

#### fn: **get_datetime**
Returns `datetime.datetime.now()`

----------

#### fn: **get_internal_ip**
Returns the local ip address of the computer

----------

#### fn: **get_external_ip**
Returns the public/external ip address of the computer

----------

#### fn: **generate_key**
Returns a _random_ string

Params:
- **value** - _Type: String/int/etc._ - _Named argument_ - Default: random int - Value to be encoded to create the return string
- **salt** - _Type: String/int/etc._ - _Named argument_ - Default: random int - Value to use to help encode the string
- **size** - _Type: Int_ - _Named argument_ - Default: 8 - Min size the return string shopuld be

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

#### fn: **get_value**
Get a value from a dict if it exists, if the key does not exist, will return `None` value
Params:

- **key** - _Type: String_ - The key you are looking for
- **object** - _Type: dict_ - The dict you are looking for said key in
- **default_value** - _Type: Any_ - Named argument, what to return if the key does not exist

Ex:
```python
test_dict = {'valA': 5, 'valB': 3}
my_val = cutil.get_value('valA', test_dict)  # Returns 5
my_val = cutil.get_value('valC', test_dict)  # Returns None
my_val = cutil.get_value('valA', test_dict, default_val=87)  # Returns 5
my_val = cutil.get_value('valC', test_dict, default_val=87)  # Returns 87
```

----------

#### fn: **get_default_header**
Returns a dict with the User Agent set to the UA Chrome uses.

----------

#### fn: **set_url_header**
Params:

- **url_header** - _Type: dict_ - Dict of header arguments, if `None`, return the value of `get_default_header()`

Returns a header passed in or the `get_default_header` header.

----------

#### fn: **make_url_safe**
Params:

- **string** - _Type: String_ - String that needs to be made safe to use in a web url

Returns the string with the converted chars, uses `urllib.parse.quote_plus(string)`

----------

#### fn: **custom_proxy_setup**
Params:

- **cb** - _Type: Function_ - Callback function to handle getting a new proxy
- **iso_country_code** - _Type: String_ - Default: `None` - This will be passed to the callback function

The callback function must return a proxy url as a string

----------

#### fn: **get_current_proxy**
If you have proxies set, it will return what the current one is

----------

#### fn: **rotate_proxy**
If you have proxies set, it will get the next one in the list and start using it. Will also return the one it chose. This works with `custom_proxy_setup` if it is used

----------

#### fn: **get_current_apikey**
If you have apikeys set, it will return what the current one is

----------

#### fn: **rotate_apikey**
If you have apikeys set, it will get the next one in the list and start using it. Will also return the one it chose.

----------

#### fn: **get_image_dimension**
Params:

- **url** - _Type: String_ - image to get WxH from

Returns 2 values `w, h`

----------

#### fn: **crop_image**
Returns the path of the cropped image

Params:
image_file, output_file=None, height=None, width=None, x=None, y=None
- **image_file** - _Type: String_ - _Positional argument_ - Path to the image to be cropped
- **output_file** - _Type: String_ - _Named argument_ - Default: `None` - **Required** Path to save the cropped image to
- **height** - _Type: Int_ - _Named argument_ - Default: `None` - **Required** Height the cropped image should be
- **width** - _Type: Int_ - _Named argument_ - Default: `None` - **Required** Width the cropped image should be
- **x** - _Type: Int_ - _Named argument_ - Default: `None` - **Required** x cord of the top left of the location to start cropping
- **y** - _Type: Int_ - _Named argument_ - Default: `None` - **Required** y cord of the top left of the location to start cropping

----------

### **cutil.RepeatingTimer**

#### fn: **`__init__`**
Params:

- **interval** - _Type: Int_ - _Positional argument_ - Duration of the timer
- **func** - _Type: Function_ - _Positional argument_ - Function to call when the timer triggers
- **repeat** - _Type: Boolean_ - _Named argument_ - Default: `True` - Should the timer reset after it is triggered

----------

#### fn: **`start`**
Start the timmer

Params:
_N/A_

----------

#### fn: **`cancel`**
Stop/disable the timmer

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

Use to get a cursor to make db calls. It will handle commiting the data and rollback if there is an error. Any error/exceptions that happen are passed back to the user
```python
try:
    with db.getcursor() as cur:
        cur.execute("SELECT * FROM table_name")
except Exception as e:
    print("Error with db call: " + str(e))
```

----------

#### fn: **insert**
Params:

- **table** - _Type: String_ - _Positional argument_ - Table that data should be inserted into. Include schema.
- **data** - _Type: List/Dict_ - _Positional argument_ - List or Dict of data to insert. List must be a list of dicts
- **id_col** - _Type: String_ - _Named argument_ - Default: 'id' - Primary key column of the table

