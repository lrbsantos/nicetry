from abc import abstractmethod, ABC
from typing import Callable, Generic, TypeVar, Union

T = TypeVar('T')
U = TypeVar('U')

class Try(ABC, Generic[T]):
    """
    The `Try` type represents a computation that may fail during evaluation by raising an exception.
    It holds either a successfully computed value or the exception that was thrown. This approach
    presents an alternative to try-except statement, by providing a more object-functional paradigm
    to deal with exceptions.

    Instances of `Try[T]` are either an instance of Success[T] or Failure[T].

    For example, `Try` can be used to perform division on a user-defined input, without
    the need to do explicit exception-handling in all of the places that an exception
    might occur.
  
    Example using try-except statement:
    >>> def divide():
    >>>   dividend = input("Enter an Int that you'd like to divide: ")
    >>>   divisor = input("Enter an Int that you'd like to divide by: ")
    >>>
    >>>   try:
    >>>       result = dividend / divisor
    >>>       print(f"Result of {dividend} / {divisor}  is {result}")
    >>>   except Exception as e:
    >>>       print("You must've divided by zero or entered something that's not an Int. Try again!")
    >>>       print(f"Info from the exception: {e}")
    >>>
    >>> divide()

    Example using Try-Success-Failure pattern:
    >>> from nicetry import Try, Success, Failure
    >>>
    >>> def divide():
    >>>   dividend = input("Enter an Int that you'd like to divide: ")
    >>>   divisor = input("Enter an Int that you'd like to divide by: ")
    >>>   result = Try.to(lambda: dividend / divisor)
    >>>
    >>>   match result:
    >>>     case Success(v):
    >>>       print(f"Result of {dividend} / {divisor}  is {v}")
    >>>     case Failure(e):
    >>>       print("You must've divided by zero or entered something that's not an Int. Try again!")
    >>>       print(f"Info from the exception: {e}")
    >>>
    >>> divide()

    An important property of Try shown in the below example is its ability to pipeline, or chain, operations,
    catching exceptions along the way. The flat_map and map combinators in the below example each essentially
    pass off either their successfully completed value, wrapped in the Success type for it to be further operated
    upon by the next combinator in the chain, or the exception wrapped in the Failure type usually to be simply
    passed on down the chain.

    >>> from nicetry import Try, Success, Failure
    >>>
    >>> def divide():
    >>>   dividend = Try.to(lambda: int(input("Enter an Int that you'd like to divide: ")))
    >>>   divisor = Try.to(lambda: int(input("Enter an Int that you'd like to divide by: ")))
    >>>   problem = dividend.flat_map(lambda x: divisor.map(lambda y: x / y))
    >>>   match problem:
    >>>     case Success(v):
    >>>       print(f"Result of {dividend} / {divisor} is: {v}")
    >>>     case Failure(e):
    >>>       print("You must've divided by zero or entered something that's not an Int. Try again!")
    >>>       print(f"Info from the exception: {e}")
    >>>
    >>> divide()

    :copyright: (c) 2023-2024 by Luiz Ricardo Belem.
    :license: MIT, see LICENSE for more details.
    """
    __slots__ = ("_value",)

    @staticmethod
    def to(f: Callable[[], T]) -> "Try[T]":
        """Factory method of a Try object.

        :param f: callable to be computed. The callable must be a lambda function with no param.

        :return: the result of evaluating the callable, wrapped as a `Success` or `Failure`.
        """
        try:
            return Success(f())
        except Exception as e:
            return Failure(e)

    @staticmethod
    def apply(f: Callable[[], T]) -> "Try[T]":
        """Factory method of a Try object, same as Try.to(<Callable>) method.

        This method only exists to conform to Scala Try API.
        """
        return Try.to(f)

    def __init__(self, value: T) -> None:
        super().__init__()
        self._value = value

    @property
    def is_failure(self) -> bool:
        """Returns `True` if the `Try` is a `Failure`, `False` otherwise.

        :return: `True` if the `Try` is a `Failure`, `False` otherwise.
        """
        return isinstance(self, Failure)

    @property
    def is_success(self) -> bool:
        """Returns `True` if the `Try` is a `Success`, `False` otherwise.

        :return: `True` if the `Try` is a `Success`, `False` otherwise.
        """
        return isinstance(self, Success)

    @property
    def value(self) -> T:
        """Returns the value from this `Success` or the exception if this is a `Failure`.

        :return: the value from this `Success` or the exception if this is a `Failure`.
        """
        return self._value

    @abstractmethod
    def get(self) -> T:
        """Returns the value from this `Success` or throws the exception if this is a `Failure`.

        :return: the value from this `Success` or throws the exception if this is a `Failure`.
        """
        raise NotImplementedError

    def failed(self) -> "Try[Exception]":
        """Inverts this `Try`. If this is a `Failure`, returns its exception wrapped in a `Success`.
        If this is a `Success`, returns a `Failure` containing an `UnsupportedOperationException`.

        :return:
        """
        return Success(self._value) if self.is_failure else Failure(UnsupportedOperationException("Success.failed"))

    def get_or_else(self, default_value: T) -> T:
        """Returns the value from this `Success` or the given `default_value` argument if this is a `Failure`.

        *Note:*: This will throw an exception if it is not a success and default throws an exception.

        :param default_value: the value to be returned if this is a `Failure`.

        :return: the value from this `Success` or the given `default_value` argument if this is a `Failure`.
        """
        return default_value if self.is_failure else self.get()

    def flat_map(self, f: Callable[[T], "Try[U]"]) -> "Try[U]":
        try:
            return f(self.get())
        except Exception as e:
            return Failure(e)

    def map(self, f: Callable[[T], U]) -> "Try[U]":
        """Maps the given function to the value from this `Success` or returns this if this is a `Failure`.

        :param f: lambda function to be mapped. The lambda function parameter is the value from this Success.

        :return: the outcome of the mapped function to the value from this `Success` or this if this is a `Failure`.

        """
        return Try.to(lambda: f(self.get())) if self.is_success else self

    def or_else(self, t: "Try[U]") -> "Try[U]":
        """Returns this `Try` if it's a `Success` or the given `default` argument if this is a `Failure`.
        """
        return self if self.is_success else t

    @abstractmethod    
    def for_each(self, f: Callable[[T], None]) -> None:
        """
        Applies the given function f if this is a Success, otherwise does nothing if this is a Failure.

        :param f: lambda function to be applied. The lambda function parameter is the object wrapped by Success.
        """
        raise NotImplementedError

    def __iter__(self) -> "Try[T]":
        return self


class Success(Try[T]):
    __slots__ = ("_has_next",)
    __match_args__ = ("_value",)

    def __init__(self, value: T) -> None:
        super().__init__(value)
        self._has_next = True

    def get(self) -> T:
        return self._value

    def for_each(self, f: Callable[[T], None]) -> None:
        return f(self.get())

    def __next__(self) -> T:
        if self._has_next:
            self._has_next = False
            return self._value
        self._has_next = True
        raise StopIteration

    def __repr__(self) -> str:
        return "Success({})".format(str(self._value))

    def __str__(self) -> str:
        return str(self._value)


class Failure(Try[Exception]):
    __slots__ = ()
    __match_args__ = ("_value",)

    def __init__(self, exception: Exception) -> None:
        super().__init__(exception)

    def get(self) -> Exception:
        raise self._value

    def for_each(self, f: Callable[[T], None]) -> None:
        pass

    def __next__(self) -> Exception:
        raise StopIteration

    def __repr__(self) -> str:
        return "Failure({})".format(str(self._value))

    def __str__(self) -> str:
        return str(self._value)


class UnsupportedOperationException(Exception):
    pass
