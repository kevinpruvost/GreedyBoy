.. _MA:

====
 MA
====

**Description**: MA (Moving Average) represents the average value on a given length (20-30 elements for GreedyBoy).

It means that if we're checking prices every 15min, we'll need 20*15min of price values to determine the first
moving average.

**Moving average formula**: ``[Sum of the elements / Number of elements]``

**Type**: ``float``