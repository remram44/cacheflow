import os
import tempfile
import requests
from urllib.parse import urlparse

from .base import Component, ComponentLoader


# TODO: More builtin components
# WriteFile: write a string to a temporary file
# ShellCommand: execute a command
# DockerCommand: execute a Docker container
# FormatString: use Python's format(), or printf-like syntax
# Checksum: check a file's checksum (or add to Download?)


class Download(Component):
    """Downloads a file.
    """
    def execute(self, inputs, temp_dir, **kwargs):
        url, = inputs['url']
        headers, = inputs.get('headers', (None,))
        if url.startswith('file://'):
            # Just point directly at file
            # Workflow steps are not supposed to change their inputs
            self.set_output('filename', url[7:])
        else:
            # Download with requests
            r = requests.get(url, headers=headers)

            # Create file with correct extension
            path = urlparse(url).path
            extension = os.path.splitext(path)[1]
            fd, filename = tempfile.mkstemp(extension, dir=temp_dir)

            # Write file to disk
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    f.write(chunk)
            os.close(fd)

            self.set_output('filename', filename)


class EmptyFile(Component):
    """Gets an empty temporary file.
    """
    def execute(self, inputs, temp_dir, **kwargs):
        suffix, = inputs.get('suffix', (None,))
        fd, filename = tempfile.mkstemp(suffix, dir=temp_dir)
        os.close(fd)
        self.set_output('filename', filename)


class BuiltinComponentsLoader(ComponentLoader):
    """Built-in components to do basic things.
    """
    TABLE = dict(
        download=Download,
        empty_file=EmptyFile,
    )

    def get_component(self, component_def):
        try:
            component = self.TABLE[component_def.get('type')]
        except KeyError:
            return None
        else:
            component_def = dict(component_def)
            component_def.pop('type', None)
            return component(**component_def)
