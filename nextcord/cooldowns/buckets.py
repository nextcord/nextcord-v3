from enum import Enum


class _HashableArguments:
    # An internal class defined such that we can
    # use *args and **kwargs as keys. We need to
    # do this as mutable items are not hashable,
    # therefore are not suitable for usage as
    # dictionary keys. Thus this wraps those
    # arguments with repr hashes used
    def __init__(self, *args, **kwargs):
        self.args: tuple = args
        self.kwargs: dict = kwargs

    def __repr__(self):
        return f"_HashableArguments(args={self.args}, kwargs={self.kwargs})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self.args == other.args and self.kwargs == other.kwargs

    def __hash__(self) -> int:
        # TODO This needs to be better suited to uniqueness and nesting
        return hash(repr(self.args) + repr(self.kwargs))


class CooldownBucket(Enum):
    """
    A collection of generic CooldownBucket's for usage
    in cooldown's across nextcord.

    Attributes
    ==========
    all
        The buckets are defined using all
        arguments passed to the :type:`Callable`
    args
        The buckets are defined using all
        non-keyword arguments passed to the :type:`Callable`
    kwargs
        The buckets are defined using all
        keyword arguments passed to the :type:`Callable`
    """

    all = 0
    args = 1
    kwargs = 2

    def process(self, *args, **kwargs):
        if self is CooldownBucket.all:
            return args, kwargs

        elif self is CooldownBucket.args:
            return args

        elif self is CooldownBucket.kwargs:
            return kwargs
