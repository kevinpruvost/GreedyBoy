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

   .. code-block::

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

   1. Go on `github.com <https://github.com/>`_ and create a **New** repository.

   .. image:: _static/repo_keys/screenshot1.png

   2. Configure & Create your repository.

   .. image:: _static/repo_keys/screenshot2.png

   3. You can now get ``repoName`` in these 2 fields.

   .. image:: _static/repo_keys/screenshot3.png

.. _dataBranchName:

++++++++++++++++
 dataBranchName
++++++++++++++++

.. warning::
   For this last step, you will need `Github Dekstop <https://desktop.github.com/>`_ or whatever form of ``Git`` you are using
   (**Git Bash**, **git (package from Linux)**, ...)

^^^^^^^^^^^^^^^^^^^^^^^^^^^
Github Desktop |:computer:|
^^^^^^^^^^^^^^^^^^^^^^^^^^^

   1. Clone the repository wherever you want

   .. image:: _static/repo_keys/screenshot4.png

   2. If you want to make GreedyBoy use the main branch of your repository you cant stop there
   and just take ``main`` as your ```dataBranchName``

   However, if you want to make another branch, then click on **Current branch**, type in the new branch name and
   click on **Create new branch**.

   .. image:: _static/repo_keys/screenshot5.png

   3. Click on **Publish branch** and get your **new branch name** as ``dataBranchName``

   .. image:: _static/repo_keys/screenshot6.png

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Git Command |:man_technologist:|
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   1. So if you want to go with brute force, go on whatever **shell** you wanna use.

   ``cd`` into the directory you want to clone your repository to.

   Then launch this command ``git clone $REPO_SSH_LINK|$REPO_HTTP_LINK``.

   .. image:: _static/repo_keys/screenshot7.png

   2. ``cd`` into your repository, ``git branch $BRANCH_NAME``, and ``git push -u origin $BRANCH_NAME``.

   .. image:: _static/repo_keys/screenshot8.png

   3. You're good to go, take ``$BRANCH_NAME`` as your ``dataBranchName``.
