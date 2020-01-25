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
