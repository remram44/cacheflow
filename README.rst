CacheFlow
=========

CacheFlow is a caching workflow engine, capable of executing dataflows while
reusing previous results where appropriate, for efficiency. It is very
extensible and can be used in many projects.

Goals
-----

* ☑  Python 3 workflow system
* ☑ Executes dataflows from JSON files
* ☐ Can also load from SQL database
* ☐ Parallel execution
* ☐ Streaming
* ☑ Extensible: can add new modules, new storage formats, new caching mechanism, new executors
* ☐ Pluggable: extensions can be installed from PyPI without forking
* ☑ Re-usable: can execute workflows by itself, but can also be embedded into applications. Some I plan on developing myself:

  * Literate programming app: snippets or modules embedded into a markdown file, which are executed on render (similar to Rmarkdown). Results would be cached, making later rendering fast
  * Integrate in some of my NYU research projects (VisTrails Vizier, D3M)

Other ideas:

* ☐ Use Jupyter kernels as backends to execute code (giving me quick access to all the languages they support)
* ☐ Isolate script execution (to run untrusted Python/... code, for example with Docker)

Non-goals
---------

* Make a super-scalable and fast workflow execution engine: I'd rather make executors based on Spark, Dask, Ray than re-implement those

Status
------

Basic structures are here, extracted from D3M. Execution works.
