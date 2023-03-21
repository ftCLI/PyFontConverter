import os
from font_converter.Lib.Font import Font


def get_fonts_list(
    input_path: str,
    allow_extensions: list = None,
    allow_ttf=True,
    allow_cff=True,
    allow_static=True,
    allow_variable=True,
) -> list:
    """
    Takes a path to a file or a folder, and returns a list of all valid font files that match the criteria

    :param input_path: The path to the font file or folder
    :type input_path: str
    :param allow_extensions: list of extensions to allow (".ttf", ".otf", ".woff", ".woff2"). If None, all extensions
        are allowed
    :type allow_extensions: list
    :param allow_ttf: True/False, defaults to True (optional). If False, TrueType fonts are not added to the list
    :param allow_cff: True/False, defaults to True (optional). If False, CFF fonts are not added to the list
    :param allow_static: If True, only static fonts will be returned, defaults to True (optional). If False, static
        fonts are not added to the list
    :param allow_variable: True/False, defaults to True (optional). If False, variable fonts are not added to the list
    :return: A list of font files that meet the criteria of the function.
    """

    files = []
    files_to_remove = []

    if os.path.isfile(input_path):
        files = [input_path]

    if os.path.isdir(input_path):
        files = [os.path.join(input_path, file) for file in os.listdir(input_path)]

    for file in files:
        try:
            font = Font(file)
            if allow_extensions is not None:
                if font.get_real_extension() not in allow_extensions:
                    files_to_remove.append(file)
                    continue

            if allow_ttf is False:
                if font.is_true_type:
                    files_to_remove.append(file)
                    continue

            if allow_cff is False:
                if font.is_cff is True:
                    files_to_remove.append(file)
                    continue

            if allow_variable is False:
                if font.is_variable:
                    files_to_remove.append(file)
                    continue

            if allow_static is False:
                if font.is_static:
                    files_to_remove.append(file)
                    continue

            del font

        except:
            files_to_remove.append(file)

    files = [f for f in files if f not in files_to_remove]

    return files


def get_output_dir(fallback_path: str, path: str = None) -> str:
    """
    If the output directory is not specified, then the output directory is the directory of the input file if the input
    is a file, or the input directory if the input is a directory

    :param fallback_path: The path to the input file or directory
    :type fallback_path: str
    :param path: The output directory, if specified
    :type path: str
    :return: The output directory.
    """
    if path is not None:
        return path
    else:
        if os.path.isfile(fallback_path):
            return os.path.dirname(fallback_path)
        else:
            return fallback_path


def check_output_dir(outputDir: str) -> (bool, Exception):
    """
    > Checks if the output directory is writable and returns True. If not, returns False and an error message

    :param outputDir: The directory to check
    :type outputDir: str
    :return: A tuple of two values, the first is a boolean, and the second is an exception.
    """
    try:
        os.makedirs(outputDir, exist_ok=True)
        return True, None
    except Exception as e:
        return False, e
