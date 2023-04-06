import os
import sys

from font_converter.Lib.Font import Font
from font_converter.Lib.click_tools import no_valid_fonts_message, generic_error_message


def check_input_path(
    input_path: str,
    allow_extensions: list = None,
    allow_ttf=True,
    allow_cff=True,
    allow_static=True,
    allow_variable=True,
):
    files = get_fonts_list(
        input_path,
        allow_extensions=allow_extensions,
        allow_ttf=allow_ttf,
        allow_cff=allow_cff,
        allow_static=allow_static,
        allow_variable=allow_variable,
    )

    if not len(files) > 0:
        no_valid_fonts_message(input_path)
        sys.exit()

    return files


def check_output_dir(input_path, output_path: None):
    """
    > Checks if the output directory is writable and returns its path. If not, exit
    :param input_path: the directory to check if output_path is None
    :param output_path: the directory to check
    :return: the output dir
    """
    # Check the output dir
    output_dir = get_output_dir(input_path, output_path)

    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "0.0"), "w"):
            pass
        os.remove(os.path.join(output_dir, "0.0"))
    except PermissionError:
        generic_error_message(f"Permission denied {output_dir}")
        sys.exit()
    except Exception as e:
        generic_error_message(f"Error: {e}")
        sys.exit()

    return output_dir


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
