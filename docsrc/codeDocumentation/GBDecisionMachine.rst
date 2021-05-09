*GBDecisionMachine*
===================

Description
-----------

Manages GreedyBoy decisions history, it creates, stores and retrieves data about them.

Decisions Table representation
++++++++++++++++++++++++++++++

+-------------------+-------+--------+---------------------+
| Date              | Price | Amount | :abbr:`Order (B/S)` |
+===================+=======+========+=====================+
| 1619222453.181015 | 0.523 | 13000  | :abbr:`B (Buy)`     |
+-------------------+-------+--------+---------------------+
| 1619226521.475621 | 0.553 | 13000  | :abbr:`S (Sell)`    |
+-------------------+-------+--------+---------------------+

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
