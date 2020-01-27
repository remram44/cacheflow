import os
import requests
import shutil
from urllib.parse import urlparse

from .base import Component, SimpleComponentLoader
from .cache.core import TemporaryFile


register = SimpleComponentLoader()


# TODO: More builtin components
# WriteFile: write a string to a temporary file
# ShellCommand: execute a command
# DockerCommand: execute a Docker container
# FormatString: use Python's format(), or printf-like syntax
# Checksum: check a file's checksum (or add to Download?)


@register(inputs=['url', 'headers'], outputs=['file'])
class Download(Component):
    """Downloads a file.
    """
    def execute(self, inputs, temp_dir, **kwargs):
        url, = inputs['url']
        headers = {}
        for header in inputs.get('headers', ()):
            name, value = header.split(':', 1)
            headers[name.strip()] = value.strip()

        # Create file with correct extension
        path = urlparse(url).path
        extension = os.path.splitext(path)[1]
        temp_file = TemporaryFile(temp_dir, suffix=extension)

        if url.startswith('file://'):
            shutil.copyfile(url[7:], temp_file.name)
        else:
            # Download with requests
            r = requests.get(url, headers=headers)

            # Write file to disk
            with open(temp_file.name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    f.write(chunk)

        self.set_output('file', temp_file)


@register(inputs=['suffix'], outputs=['file'])
class EmptyFile(Component):
    """Gets an empty temporary file.
    """
    def execute(self, inputs, temp_dir, **kwargs):
        suffix, = inputs.get('suffix', (None,))
        temp_file = TemporaryFile(temp_dir, suffix=suffix)
        self.set_output('file', temp_file)


@register(inputs=['file'], outputs=['table'])
class ReadCsv(Component):
    """Read a CSV file into a DataFrame.
    """
    def execute(self, inputs, **kwargs):
        import pandas

        file, = inputs['file']
        self.set_output('table', pandas.read_csv(file.name))


@register(inputs=['table', 'columns'], outputs=['table'])
class FilterColumns(Component):
    """Get specific columns from a DataFrame.
    """
    def execute(self, inputs, **kwargs):
        table, = inputs['table']
        columns, = inputs['columns']
        TODO


@register(inputs=['table', 'expression'], outputs=['table'])
class FilterRows(Component):
    """Filter rows using a Python expression.
    """
    def execute(self, inputs, **kwargs):
        table, = inputs['table']
        expression, = inputs['expression']
        TODO


@register(
    inputs=['left_table', 'right_table', 'left_column', 'right_column'],
    outputs=['table'],
)
class Join(Component):
    """Join two tables.
    """
    def execute(self, inputs, **kwargs):
        left_table, = inputs['left_table']
        right_table, = inputs['right_table']
        left_column, = inputs.get('left_column', (None,))
        right_column, = inputs.get('right_column', (None,))

        if left_column is None and right_column is None:
            raise KeyError("Both left_column and right_column are unspecified")
        elif left_column is not None and right_column is None:
            right_column = left_column
        elif left_column is None and right_column is not None:
            left_column = right_column

        result = left_table.join(right_table, TODO)
        self.set_output('table', result)


@register(inputs=['table', 'target_column'], outputs=['model'])
class TrainSvm(Component):
    """Train an SVM model.
    """
    def execute(self, inputs, **kwargs):
        from sklearn.svm import SVC

        table, = inputs['table']
        model = SVC()
        model.fit(TODO)
        self.set_output('model', model)


@register(inputs=['table', 'model'], outputs=['table'])
class Predict(Component):
    """Use a trained model.
    """
    def execute(self, inputs, **kwargs):
        table, = inputs['table']
        model, = inputs['model']
        result = model.predict(TODO)
        self.set_output('table, result')
