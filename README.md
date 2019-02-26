PyAssembly
===============================
pyassembly is the Python setup.py command. If you are familiar with fat or uber jar, than this command will come as no surprise for you. By installing and using it, you will get an "uber" egg or zip file, which will contain not only your project, but will also include all the dependencies you specified in you requirements.txt file, including the dependence of the dependencies (a.k.a. transitive dependencies), making it easy to create a self-contained distribution.


Installing
----------

.. code-block:: shell

	$ pip install pyassembly
	
Alternatively, you can include it into your requirements.txt file.


How to use
----------
Example for using the tool

.. code-block:: shell

	$ python setup.py pyassembly


How to get more options
-----------------------
After you installed the command you can get the list of options

.. code-block:: shell

	$ python setup.py pyassembly --help


Reporting Issues
----------------
If you have suggestions, bugs or other issues with this command - please open an issue or make a pull request.
