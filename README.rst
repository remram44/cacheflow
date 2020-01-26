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
