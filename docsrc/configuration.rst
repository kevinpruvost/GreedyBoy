.. _Configuration:

***********************
Configuration |:tools:|
***********************

===================
 config.csv
===================

Configuring ``config.csv`` is a mandatory step to make GreedyBoy able to work on its own.

``config.csv`` is formatted.... like a csv file.

--------------------------------------
 Table representation |:man_teacher:|
--------------------------------------

   +------------------------+--------------------------------------+----------------------------------+-------------------------------------------+----------------------------------------+
   | :ref:`apiKey <apiKey>` | :ref:`apiPrivateKey <apiPrivateKey>` | :ref:`githubToken <githubToken>` | :ref:`repoName <repoName>`                | :ref:`dataBranchName <dataBranchName>` |
   +========================+======================================+==================================+===========================================+========================================+
   | ``Api_Key``            | ``Api_Private_Key``                  | ``Github_Token``                 | kevinpruvost/GreedyBoy (**for instance**) | data (**for instance**)                |
   +------------------------+--------------------------------------+----------------------------------+-------------------------------------------+----------------------------------------+

-------------------------------------
 File representation |:file_folder:|
-------------------------------------

   .. code-block:: csv

      apiKey,apiPrivateKey,githubToken,repoName,dataBranchName
      `Api_Key`,`Api_Private_Key`,`Github_Token`,kevinpruvost/GreedyBoy,data

------------------------------------------------
How to get these informations |:card_file_box:|
------------------------------------------------

.. warning::
   Get yourself a `Kraken <https://www.kraken.com/>`_ account because GreedyBoy can't work without it.

   And also if you don't have a `Github <https://github.com/>`_ account, create one.

   In case you didn't have a Github account, then you'll be considered `sussy <https://www.youtube.com/watch?v=AIRNw9jaZro&ab_channel=kraccbacc>`_ from now on.

.. _apiKey:

.. _apiPrivateKey:

++++++++++++++++++++++++
 apiKey & apiPrivateKey
++++++++++++++++++++++++

      1. Go on `Kraken Overview <https://www.kraken.com/u/trade#tab=overview>`_ and click on your **Name, Security and API**

      .. image:: _static/apikey/screenshot1.png

      2. Click on **Add key**

      .. image:: _static/apikey/screenshot2.png

      3. For the permissions, pick **Query Funds, Query Open Orders & Trades, Query Closed Orders & Trades**,
      **Create & Modify Orders, Cancel/Close Orders and Access Websockets API**

      .. image:: _static/apikey/screenshot3.png

      4. Then you can finally access your **API Key and API Private Key**

      .. image:: _static/apikey/screenshot4.png

.. _githubToken:

+++++++++++++
 githubToken
+++++++++++++

   1. Go in `here <https://github.com/settings/tokens>`_ and click on **Generate new token**

   .. image:: _static/github_token/screenshot1.png

   2. Type in **Note** any name you want, just not something too sussy. Then check **repo** for the scopes

   .. image:: _static/github_token/screenshot2.png

   3. Then go down the page and click on **Generate token**

   .. image:: _static/github_token/screenshot3.png

   4. Then it's good to go, you got your **Github Token**!

   .. image:: _static/github_token/screenshot4.png

.. _repoName:

++++++++++
 repoName
++++++++++

   1.

.. _dataBranchName:

++++++++++++++++
 dataBranchName
++++++++++++++++

   1.