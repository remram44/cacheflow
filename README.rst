CacheFlow
=========

CacheFlow is a caching workflow engine, capable of executing dataflows while
reusing previous results where appropriate, for efficiency. It is very
extensible and can be used in many projects.

Goals
-----

* ☑ Python 3 workflow system
* ☑ Executes dataflows from JSON or YAML files
* ☐ `Can also load from SQL database <https://gitlab.com/remram44/cacheflow/issues/4>`__
* ☐ `Parallel execution <https://gitlab.com/remram44/cacheflow/issues/14>`__
* ☐ `Streaming/batching <https://gitlab.com/remram44/cacheflow/issues/13>`__
* ☑ Extensible: can add new components, new storage formats, new caching mechanism, new executors
* ☐ Pluggable: extensions can be installed from PyPI without forking
* ☑ Re-usable: can execute workflows by itself, but can also be embedded into applications. Some I plan on developing myself:

  * ☑ `Literate programming app <https://gitlab.com/remram44/cacheflow/issues/2>`__: snippets or components embedded into a markdown file, which are executed on render (similar to Rmarkdown). Results would be cached, making later rendering fast
  * ☐ Integrate in some of my NYU research projects (VisTrails, Vizier, D3M)

* ☐ `Web-based interface allowing collaborative edition of workflows, with automatic re-execution on change <https://gitlab.com/remram44/cacheflow/issues/11>`__

Other ideas:

* ☐ Use Jupyter kernels as backends to execute code (giving me quick access to all the languages they support)
* ☐ Isolate script execution (to run untrusted Python/... code, for example with Docker)

Non-goals
---------

* Make a super-scalable and fast workflow execution engine: I'd rather `make executors based on Spark, Dask, Ray <https://gitlab.com/remram44/cacheflow/issues/14>`__ than try to re-implement those from scratch.

Status
------

Basic structures are here, extracted from D3M. Execution works. Very few components available. Working on web interface.

Development setup
-----------------

Set up the Python package:

* I use the Poetry package manager for Python; first you'll have to `install Poetry <https://python-poetry.org/docs/#installation>`__
* Create the Python environment with ``poetry env use python3.7``
* Install the package with ``poetry install``
* You can then use ``poetry run <cacheflow|noteflow|python ...>``
* Run the tests with ``poetry run python tests``

Set up the web interface:

* Two choices:

  * If you have NodeJS and Yarn installed, you can install Vue with ``npm install -g @vue/cli`` and then run the development server with ``yarn serve --port 8000``
  * If you would rather not mess with Node and just use Docker, you can do ``make build-image`` and run the development server with ``make serve``

* In both cases, you need to run Cacheflow's API server with ``poetry run cacheflow-web``. You can then go to `http://localhost:8000/ <http://localhost:8000/>`__
