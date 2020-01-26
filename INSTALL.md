Development setup
=================

Set up the Python package:

* I use the Poetry package manager for Python; first you'll have to [install Poetry](https://python-poetry.org/docs/#installation>)
* Create the Python environment with `poetry env use python3.7`
* Install the package with `poetry install`
* You can then use `poetry run <cacheflow|noteflow|python ...>`
* Run the tests with `poetry run python tests`

Set up the web interface:

* Two choices:
  * If you have NodeJS and Yarn installed, you can install Vue with `npm install -g @vue/cli` and then run the development server with `make serve-local`
  * If you would rather not mess with Node and just use Docker, you can do `make build-image` and run the development server with `make serve`
* In both cases, you need to run Cacheflow's API server with `poetry run cacheflow-web`. You can then go to [`http://localhost:8000/`](http://localhost:8000/)

Build for release
=================

* I use the Poetry package manager for Python; first you'll have to [install Poetry](https://python-poetry.org/docs/#installation>)
* Build the web UI. Two choices:
  * If you have NodeJS and Yarn installed, you can install Vue with `npm install -g @vue/cli` and then build with `make build-local`
  * If you would rather not mess with Node and just use Docker, you can do `make build-image` and build with `make build`
* Build the Python package with `poetry build`
