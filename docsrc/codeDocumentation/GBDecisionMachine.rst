*GBDecisionMachine*
===================

Description
-----------

Manages GreedyBoy decisions history, it creates, stores and retrieves data about them.

Decisions Table representation
++++++++++++++++++++++++++++++

+-------------------+-------+--------+--------------------------+
| Date              | Price | Amount | :abbr:`Order (buy/sell)` |
+===================+=======+========+==========================+
| 1619222453.181015 | 0.523 | 13000  | :abbr:`buy`              |
+-------------------+-------+--------+--------------------------+
| 1619226521.475621 | 0.553 | 13000  | :abbr:`sell`             |
+-------------------+-------+--------+--------------------------+

Decisions CSV representation
++++++++++++++++++++++++++++

.. code-block::

   Date,Price,Amount,Order
   1619222453.181015,0.523,13000,B
   1619226521.475621,0.553,13000,S

Code
----

.. automodule:: GBDecisionMachine
   :members:
   :undoc-members:
