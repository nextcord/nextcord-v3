from typing import Any


class CooldownBucket:
    """
    A collection of generic CooldownBucket's for usage
    in cooldown's across nextcord.
    """

    @classmethod
    async def args(cls, *args: Any, **kwargs: Any) -> bool:
        """
        Implements cooldown's based on the non-keyword arguments
        that the wrapped :type:`Callable` takes.

        Returns
        -------
        bool
            Returns True if this is not on cooldown.

        Raises
        ------

        """
