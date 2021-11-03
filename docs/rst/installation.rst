Installation
------------

The package is distributed via `pypi <https://pypi.org/project/structuralglass/>`_. 
Installing from this source will provide all dependencies.

.. code-block:: text

    $ pip install structuralglass

When reproducibility is a concern, we recommend installing this library within a virtual environment and creating a 
requirements file that sets the dependencies. For example (on Linux):

1. Create a virtual environment:

.. code-block:: text

    $ python -m venv .env

2. Activate the virtual environment:

.. code-block:: text
    
    $ source .env/bin/activate

3. Create a requirements file:

.. code-block:: text

    # requirements.txt
    pint==0.17
    scipy==1.7.0
    numpy==1.21.1
    structuralglass==0.02

4. Install using the requirements file:

.. code-block:: text

    $ pip install -r requirements.txt
