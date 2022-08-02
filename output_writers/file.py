import datetime
import os
import json

OUTPUT_FILES_DIRECTORY = 'outputs'


class FileWriter:
    def __init__(self):
        self._ensure_directory()
        self.filename = self._generate_filename()
        self.file = open(f'{OUTPUT_FILES_DIRECTORY}/{self.filename}', 'w')


    def _ensure_directory(self):
        if not os.path.exists(OUTPUT_FILES_DIRECTORY):
            os.makedirs(OUTPUT_FILES_DIRECTORY)

    def _generate_filename(self):
        date = datetime.datetime.now()

        filename = (f'{date.year}{date.month:2}{date.day:2}{date.hour:2}'
                    f'{date.minute:2}')
        return filename

    def write_item(self, post: dict):
        output_units = []
        for k, v in post.items():
            output_units.append(f'{v};')
        output_units.append('\n')
        output_str = ''.join(output_units)
        self.file.write(output_str)

    def flush(self):
        self.file.close()

