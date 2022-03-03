from typing import Protocol, Any


class BucketProtocol(Protocol):
    """BucketProtocol implementation Protocol."""

    def process(self, *args, **kwargs) -> Any:
        """

        Returns
        -------
        Any
            The values returned from this method
            will be used to represent a bucket.
        """
        ...
