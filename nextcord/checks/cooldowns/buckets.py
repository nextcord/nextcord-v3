import math
from enum import Enum
from collections import Hashable
from typing import Any, Union, Optional

from ...exceptions import InteractionBucketFailure


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

    @staticmethod
    def __get_hash(item: Union[Hashable, Any]):
        if not isinstance(item, Hashable):
            item = repr(item)

        return hash(item)

    def __hash__(self) -> int:
        """
        Hashing strategy.

        If we are wrapping nothing, well, -_-
        return the hash of a constant.

        If we are hashing *args, we can simply
        return the hash of the containing tuple
        and let python deal with it.

        If we are hashing **kwargs we hash
        a tuple of tuples, in the form
        ((key, value), ...)

        For *args and **kwargs we combine
        both approaches for the format:
        (*args, (key, value), ...)
        """
        has_args: bool = bool(self.args)
        has_kwargs: bool = bool(self.kwargs)
        if not has_args and not has_kwargs:
            # I'd like a better solution / constant
            return hash(math.pi)

        if has_args and not has_kwargs:
            # Hash the tuple and let python deal with it
            return hash(self.args)

        if not has_args and has_kwargs:
            # Has kwargs as a tuple of tuples
            rolling_hash = []
            for k, v in self.kwargs.items():
                rolling_hash.append((k, v))

            return hash(tuple(rolling_hash))

        # Same as for kwargs, but with args in it
        rolling_hash = [*self.args]
        for k, v in self.kwargs.items():
            rolling_hash.append((k, v))

        return hash(tuple(rolling_hash))


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

        # TODO Implement these once slash is in

    #     elif self is CooldownBucket.interaction_author:
    #         # TODO Is args[0] self in classes?
    #         inter: Interaction = self.__ensure_interaction(args[0])
    #         return inter.user.id
    #
    #     elif self is CooldownBucket.interaction_channel:
    #         inter: Interaction = self.__ensure_interaction(args[0])
    #         return inter.channel.id
    #
    #     elif self is CooldownBucket.interaction_guild:
    #         inter: Interaction = self.__ensure_interaction(args[0])
    #         return inter.guild.id
    #
    # @staticmethod
    # def __ensure_interaction(item: Optional[Interaction]) -> Interaction:
    #     if not isinstance(item, Interaction):
    #         raise InteractionBucketFailure
    #
    #     return item
