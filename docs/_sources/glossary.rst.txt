Glossary
**************************
.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. _MA:

====
 MA
====

**Description**: MA (Moving Average) represents the average value on a given length (20-30 elements for GreedyBoy).

It means that if we're checking prices every 15min, we'll need 20*15min of price values to determine the first
moving average.

**Moving average formula**: :math:`MA = \frac{Sum\ of\ elements}{Number\ of\ elements}`

**Type**: ``float``

.. _Std:

=====
 Std
=====

**Description**: Std (Standard Deviation) represents the standard deviation on a given length (20-30 elements for GreedyBoy).

It means that if we're checking prices every 15min, we'll need 20*15min of price values to determine the first
standard deviation.

**Standard Deviation formula**: :math:`Std = \sqrt{\frac{Sum\ of\ squared\ deviation\ from\ MA\ of\ every\ elements}{Number\ of\ elements}}`

**Type**: ``float``

.. _HBand:

=======
 HBand
=======

**Description**: HBand (Higher Band) represents the higher bollinger band.

It means that if the Close price is going over this band, then the price is rising
at an abnormal rate.

**Higher Band formula**: :math:`HBand = MA + Std * 2`

**Type**: ``float``

.. _LBand:

=======
 LBand
=======

**Description**: LBand (Lower Band) represents the lower bollinger band.

It means that if the Close price is going under this band, then the price is dipping
at an abnormal rate.

**Lower Band formula**: :math:`LBand = MA - Std * 2`

**Type**: ``float``