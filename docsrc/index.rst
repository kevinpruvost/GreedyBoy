.. GreedyBoy master file, created by
   sphinx-quickstart on Fri Apr 30 12:12:26 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========
GreedyBoy
=========

.. image:: _static/screenshot.png
    :alt: GreedyBoy Screenshot

GreedyBoy is an automated trading bot specialized in cryptocurrencies trading.

Specifications
--------------

APIs
++++
For now, `Kraken <https://docs.kraken.com/websockets/>`_ is the only market API implemented.

GreedyBoy can only perform orders and retrieve informations from this one.

Cryptocurrencies
++++++++++++++++
GreedyBoy is virtually able to perform analysis on any cryptocurrency.

But for now we are focused on these cryptocurrencies:

==============  =========  =============
Cryptocurrency  Full Name  CoinmarketCap
==============  =========  =============
BTC             Bitcoin     `BTC <https://coinmarketcap.com/fr/currencies/bitcoin/>`_
ETH             Ethereum    `ETH <https://coinmarketcap.com/fr/currencies/ethereum/>`_
XRP             Ripple      `XRP <https://coinmarketcap.com/fr/currencies/ripple/>`_
DOGE            Dogecoin    `DOGE <https://coinmarketcap.com/fr/currencies/dogecoin/>`_
==============  =========  =============

Implementation
--------------

If you don't want to follow the text tutorial here's, first, the video tutorial.

.. raw:: html

    <div style="text-align: center; margin-bottom: 2em;">
    <iframe width="100%" height="500" src="https://www.youtube-nocookie.com/embed/GlOQnsVOa2o?rel=0" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
    </div>

`AWS Lambda <https://aws.amazon.com/fr/lambda/>`_
+++++++++++++++++++++++++++++++++++++++++++++++++

`Kraken <www.kraken.com>`_
++++++++++++++++++++++++++

Documentation
-------------

.. toctree::
   :maxdepth: 3
   :caption: Summary

   ./code.rst


==================
Indices and tables
==================
- :ref:`genindex`
- :ref:`modindex`