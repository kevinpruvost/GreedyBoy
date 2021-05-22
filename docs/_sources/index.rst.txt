.. GreedyBoy master file, created by
   sphinx-quickstart on Fri Apr 30 12:12:26 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========
GreedyBoy
=========

.. image:: _static/graphViewer.png

GreedyBoy is an automated trading bot specialized in cryptocurrencies trading.

Specifications
--------------

APIs
++++
For now, the `Kraken API <https://docs.kraken.com/websockets/>`_ is the only market API implemented.

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

Setup
-----

.. toctree::
   :maxdepth: 2

   ./installation.rst
   ./configuration.rst

Documentation
-------------

.. toctree::
   :maxdepth: 2

   ./code.rst
   ./glossary.rst


==================
Indices and tables
==================
- :ref:`genindex`
- :ref:`modindex`