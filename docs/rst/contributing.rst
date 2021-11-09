How to Contribute
-----------------
The code repository is hosted on `GitHub <https://github.com/normanrichardson/structuralglass>`_.
To contribute fixes, code, or documentation, fork the repository and submit changes using a pull request against the master branch.

Set Up Your Environment
=======================
We recommend developing within a virtual environment.
The following installation is recommended within the virtual environment:

.. code-block::

    $ git clone <url to forked repo> structuralglass
    $ cd structuralglass
    $ pip install -e .[dev]

Using the `dev` option will add additional dependencies for development, such as Sphinx, flake8, black, and isort.

If distribution dependencies are needed add the `dist` option:

.. code-block::

    $ pip install -e .[dev,dist]

Testing
=======
The test suite can be run with:

.. code-block::
    
    $ python -m unittest test.unittests
