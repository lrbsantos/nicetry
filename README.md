# NiceTry
A Python type for the classic try-except statement that allows a more functional and declarative approach to handle exceptions.

Inspired by [Scala Try API](https://www.scala-lang.org/api/current/scala/util/Try.html), originally implemented by [Twitter](https://twitter.com/)'s software engineers.

Licensed under the [MIT License](https://opensource.org/license/mit).

The `Try` type represents a computation that may fail throwing an exception. If the computation is successful it returns the value wrapped in a `Success` otherwise an Exception wrapped in a `Failure`.

To use `Try` you need to call the `Try.to(f: Callable)` method providing a lambda function with no parameters that invokes the method that may raise an exception.

## Features

- 100% pure Python
- support to [structural pattern matching](https://peps.python.org/pep-0636/) (`match` statement)
- conform to original Scala Try API

## Basics
`Try` represents the successful or failed outcome of an operation and might contain a value that was produced by said operation.

```python
from nicetry import Try
result = Try.to(lambda: 4 / 1)
```

The above example would evaluate `4 / 1` and, because that does not throw an exception, return a `Success` and store it in the variable `result`. The result of the calculation is stored inside the `Success` and can be accessed using several methods.

```python
print(result.value)
print(result.get())
```

To find out if `result` represents success or failure, it provides the boolean properties `is_success` and `is_failure`:

```python
if result.is_success:
    print(result.get())
```

The below example shows how we can deal with failures.

```python
result = Try.to(lambda: 1 / 0)
if result.is_failure:
    print("Ooops, something bad happened!")
```

When the result of the calculation is a `Failure`, the `value` property and the `get()` method differ slightly. The `value` property returns the Exception object, while the `get()` method throws the exception. This behavior conforms to the original Scala Try API.

```python
result.value
result.get()
```

## Usage

### Creating a Try
There are several ways to create an instance of `Try`.

#### Try.to(f: Callable) method
Evaluates a lambda function synchronously and returns a `Success` if no exception is thrown or a `Failure` otherwise.

```python
Try.to(lambda: 4 / 2)
Try.to(lambda: 4 / 0)
```

#### Try.apply(f: Callable) method
Does the same as `Try.to()` method. This method only exists to conform to the original Scala Try API.

```python
Try.apply(lambda: 4 / 2)
Try.apply(lambda: 4 / 0)
```

### Accessing the wrapped value or exception
`Try` implements a couple of methods to access the wrapped value or exception.

#### `value` property
Returns the value from the `Try` if this `Success` or the exception if this is a `Failure`.

```python
Try.to(lambda: 4 / 2).value
Try.to(lambda: 4 / 0).value
```

#### `get()` method
Returns the value from the `Try` if this `Success` or throws the exception if this is a `Failure`.

```python
Try.to(lambda: 4 / 2).get()
Try.to(lambda: 4 / 0).get()
```

Note that the `value` property and the `get()` method differ slightly when `Try` is a `Failure`. The `value` property returns the Exception object, while the `get()` method throws an exception. This behavior conforms to the original Scala Try API.

## Examples
In order to get you acquainted with this API each example will be provided using both the same old `try-except` statement and the new Try-Success-Failure pattern.

### Example 1: Read the HTML content of an URL ###
As a first example consider you need to implement a method that reads the HTML content of an URL as string.

#### Using the traditional try-except statement ####
```python
from urllib import request

def read_content(url: str, error_message: str = "Oops, something bad happened!") -> str:
    try:
        with request.urlopen(url) as req:
            return req.read().decode('utf-8')
    except:
        return error_message

read_content("https://mofanpy.com/static/scraping/basic-structure.html")
read_content("https://mofanpy.com/static/scraping/basic-structure.xhtml")
```

#### Using the Try API (object-oriented approach) ####
```python
from urllib import request
from nicetry import Try

def read_content(url: str, error_message: str = "Oops, something bad happened!") -> str:
    resp = Try.to(lambda: request.urlopen(url))
    if resp.is_success:
        with resp.get() as req:
            return req.read().decode('utf-8')
    else:
        return error_message

read_content("https://mofanpy.com/static/scraping/basic-structure.html")
read_content("https://mofanpy.com/static/scraping/basic-structure.xhtml")
```

#### Using the Try API (structural pattern matching approach) ####
```python
from urllib import request
from nicetry import Try, Success, Failure

def read_content(url: str, error_message: str = "Oops, something bad happened!") -> str:
    match Try.to(lambda: request.urlopen(url)):
        case Success(req):
            with req:
                return req.read().decode('utf-8')
        case Failure(_):
            return error_message

read_content("https://mofanpy.com/static/scraping/basic-structure.html")
read_content("https://mofanpy.com/static/scraping/basic-structure.xhtml")
```

#### Using the Try API (functional approach) ####
```python
from urllib import request
from nicetry import Try

def read_content(url: str, error_message: str = "Oops, something bad happened!") -> str:
    resp = Try.to(lambda: request.urlopen(url))
    result = resp.map(lambda r: r.read().decode('utf-8')).get_or_else(error_message)
    resp.for_each(lambda r: r.close())
    return result

read_content("https://mofanpy.com/static/scraping/basic-structure.html")
read_content("https://mofanpy.com/static/scraping/basic-structure.xhtml")
```

## TODO

- [ ] support to Python [context manager](https://docs.python.org/3/reference/datamodel.html#context-managers) (the [with](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement) statement)
- [ ] implement the remaining Scala Try API methods
