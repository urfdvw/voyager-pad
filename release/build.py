#!/Users/river/mambaforge/bin/python

import pathlib
import zipfile

ignore = [
    '.DS_Store',
    'settings.json',
    'boot_out.txt'
]

directory = pathlib.Path("./src")


with zipfile.ZipFile("./release/latest.zip", mode="w") as archive:
    for file_path in directory.rglob("*"):
        for f in ignore:
            if str(file_path).endswith(f):
                break
        else:
            print(file_path)
            archive.write(
                file_path,
                arcname=file_path.relative_to(directory)
            )

print('done packing')