.. nextcord documentation master file, created by
   sphinx-quickstart on Sun Dec  5 16:40:28 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to nextcord's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

This is a codeblock style test:
-------------------------------

.. code-block:: python3

   from typing import Iterator

   # This is an example
   class Math:
      @staticmethod
      def fib(n: int) -> Iterator[int]:
         """ Fibonacci series up to n """
         a, b = 0, 1
         while a < n:
            yield a
            a, b = b, a + b

   result = sum(Math.fib(42))
   print("The answer is {}".format(result))
