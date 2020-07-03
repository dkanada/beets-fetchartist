"""
Utility functions for the fetchartist plugin.
"""
import os

def strip_template_path_suffix(template, marker_string):
    """
    Removes the filename from a path template and strips the remaining suffix
    until the folder that contains the given marker string. If the marker
    string is not found, the path without the filename is returned.
    """
    template_folder = os.path.dirname(template)
    index = template_folder.rfind(marker_string)

    if index == -1:
        return template_folder

    first_slash = template_folder.find("/", index)
    if first_slash == -1:
        return template_folder

    return template_folder[0:first_slash]

def find_existing_and_missing_files(paths, extensions=None):
    """
    Returns whether files at the given paths with the given extensions exist. A
    tuple of existing and missing files is returned. The first element of the
    tuple is a dictionary that maps a path without extension to all extensions
    that concatenated with the path point to an existing file. The second
    element of the tuple contains all paths without extensions where no file exists.
    """
    extensions = extensions or set({""})

    existing_paths = dict()
    missing_paths = set()

    for path in paths:
        is_missing = True
        for extension in extensions:
            if os.path.isfile(path + "." + extension):
                path_extensions = existing_paths.get(path)
                if not path_extensions:
                    path_extensions = list()
                    existing_paths[path] = path_extensions

                path_extensions.append(extension)
                is_missing = False
        if is_missing:
            missing_paths.add(path)

    return (existing_paths, missing_paths)
