import os
import time

import click
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.ttLib import TTCollection, TTLibError
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from pathvalidate import sanitize_filename

from font_converter.Lib.Font import Font
from font_converter.Lib.cli_tools import get_fonts_list, get_output_dir, check_output_dir
from font_converter.Lib.click_tools import (
    add_file_or_path_argument,
    add_common_options,
    generic_error_message,
    no_valid_fonts_message,
    generic_info_message,
    file_saved_message, select_instance_coordinates, generic_warning_message,
)
from font_converter.Lib.converters import otf_to_ttf
from font_converter.Lib.converters.ttf_to_otf import TrueTypeToCFF


@click.group()
def ttf_2_otf():
    pass


@ttf_2_otf.command()
@add_file_or_path_argument()
@click.option(
    "-t",
    "--tolerance",
    type=click.FloatRange(0, 5),
    default=1,
    help="""
    Conversion tolerance (0-5, default 1). Low tolerance adds more points but keeps shapes. High tolerance adds few
    points but may change shape.
    """,
)
@click.option(
    "--safe",
    is_flag=True,
    help="""
    Sometimes Qu2CuPen may fail or produce distorted outlines. Most of times, using '--safe' will prevent errors by
    converting the source TTF font to a temporary OTF built using T2CharstringsPen, and then reconverting it to a
    temporary TTF font. This last one will be used for TTF to OTF conversion instead of the source TTF file. This is
    slower and produces slightly bigger files, but is safer.
    """,
)
@click.option(
    "--keep-glyphs",
    "purge_glyphs",
    is_flag=True,
    default=True,
    help="""
    Doesn't remove 'NULL' and 'CR' glyphs from the output font.
    """,
)
@click.option(
    "--no-subr",
    "subroutinize",
    is_flag=True,
    default=True,
    help=""" 
    Turn off subroutinization of converted fonts.
    """,
)
@add_common_options()
def ttf2otf(input_path, tolerance, safe, purge_glyphs, subroutinize, recalcTimestamp, outputDir, overWrite):
    """
    Converts fonts from TrueType to CFF format.
    """
    files = get_fonts_list(input_path, allow_variable=False, allow_cff=False)
    if len(files) == 0:
        no_valid_fonts_message(input_path)
        return

    output_dir = get_output_dir(fallback_path=input_path, path=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)

    start_time = time.time()
    converted_files_counter = 0
    counter = 0

    for file in files:
        t = time.time()
        counter += 1

        try:
            output_file = makeOutputFileName(file, extension=".otf", outputDir=output_dir, overWrite=overWrite)

            if safe:
                # Create a temporary file...
                temp_otf_file = makeOutputFileName(output_file, suffix="_tmp", overWrite=True)
                ttf2otf_converter_temp = TrueTypeToCFF(
                    input_file=file, output_file=temp_otf_file, recalc_timestamp=recalcTimestamp
                )
                ttf2otf_converter_temp.run(
                    charstrings_source="t2", purge_glyphs=purge_glyphs, subroutinize=False, overwrite=True
                )

                # And convert it back to a temporary TTF file that will be used for conversion
                temp_ttf_file = makeOutputFileName(temp_otf_file, extension=".ttf", overWrite=True)
                otf_to_ttf.run(input_file=temp_otf_file, output_file=temp_ttf_file, recalc_timestamp=recalcTimestamp)
                os.remove(temp_otf_file)
                input_file = temp_ttf_file
            else:
                input_file = file

            print()
            generic_info_message(f"Converting file {os.path.basename(file)}: {counter} of {len(files)}")

            ttf2otf_converter = TrueTypeToCFF(
                input_file=input_file, output_file=output_file, recalc_timestamp=recalcTimestamp
            )
            ttf2otf_converter.run(
                charstrings_source="qu2cu",
                tolerance=tolerance,
                overwrite=overWrite,
                subroutinize=subroutinize,
                purge_glyphs=purge_glyphs,
            )

            if safe:
                os.remove(input_file)

            converted_files_counter += 1
            generic_info_message(f"Done in {round(time.time() - t, 3)} seconds")
            file_saved_message(ttf2otf_converter.output_file)

        except Exception as e:
            generic_error_message(e)

    print()
    generic_info_message(f"Total files       : {len(files)}")
    generic_info_message(f"Converted files   : {converted_files_counter}")
    generic_info_message(f"Elapsed time      : {round(time.time() - start_time, 3)} seconds")


@click.group()
def otf_2_ttf():
    pass


@otf_2_ttf.command()
@add_file_or_path_argument()
@add_common_options()
def otf2ttf(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Converts fonts from CFF to TrueType format.
    """

    files = get_fonts_list(input_path, allow_ttf=False, allow_variable=False)
    if len(files) == 0:
        generic_error_message(f"No valid font files found in {input_path}.")
        return

    output_dir = get_output_dir(fallback_path=input_path, path=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    start_time = time.time()
    counter = 0
    converted_files = 0

    for file in files:
        t = time.time()
        counter += 1

        generic_info_message(f"Converting file {counter} of {len(files)}")
        try:
            output_file = makeOutputFileName(
                file, outputDir=output_dir, overWrite=overWrite, extension=".ttf"
            )
            otf_to_ttf.run(
                input_file=file,
                output_file=output_file,
                recalc_timestamp=recalcTimestamp,
            )
            converted_files += 1
            generic_info_message(f"Done in {round(time.time() - t, 3)}")
            file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)

    print()
    generic_info_message(f"Total files       : {len(files)}")
    generic_info_message(f"Converted files   : {converted_files}")
    generic_info_message(f"Elapsed time      : {round(time.time() - start_time, 3)} seconds")


@click.group()
def web_to_sfnt():
    pass


@web_to_sfnt.command()
@add_file_or_path_argument()
@click.option(
    "-f",
    "--flavor",
    type=click.Choice(choices=["woff", "woff2"]),
    help="""
              By default, the script converts both woff and woff2 flavored web fonts to SFNT fonts (TrueType or
              OpenType). Use this option to convert only woff or woff2 flavored web fonts.
              """,
)
@click.option(
    "-d",
    "--delete-source-file",
    is_flag=True,
    help="""
              Deletes the source files after conversion.
              """,
)
@add_common_options()
def wf2ft(
    input_path,
    flavor=None,
    delete_source_file=False,
    outputDir=None,
    recalcTimestamp=False,
    overWrite=True,
):
    """
    Converts web fonts (WOFF and WOFF2) to SFNT fonts (TTF or OTF).
    """

    files = get_fonts_list(input_path, allow_extensions=[".woff", ".woff2"])
    if len(files) == 0:
        generic_error_message(f"No valid font files found in {input_path}.")
        return

    output_dir = get_output_dir(fallback_path=input_path, path=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for file in files:
        try:
            web_font = Font(file, recalcTimestamp=recalcTimestamp)
            if web_font.flavor is None:
                continue
            if flavor is not None:
                if web_font.flavor != flavor:
                    continue
            web_font.flavor = None
            extension = web_font.get_real_extension()
            desktop_font_file = makeOutputFileName(
                file, extension=extension, outputDir=output_dir, overWrite=overWrite
            )
            web_font.save(desktop_font_file, reorderTables=False)
            if delete_source_file:
                os.remove(file)
            file_saved_message(desktop_font_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def sfnt_to_web():
    pass


@web_to_sfnt.command()
@add_file_or_path_argument()
@click.option(
    "-f",
    "--flavor",
    type=click.Choice(choices=["woff", "woff2"]),
    help="""
              By default, the script converts SFNT fonts (TrueType or OpenType) both to woff and woff2 flavored web
              fonts. Use this option to create only woff (--flavor woff) or woff2 (--flavor woff2) files.
              """,
)
@add_common_options()
def ft2wf(
    input_path, flavor=None, outputDir=None, recalcTimestamp=False, overWrite=True
):
    """
    Converts SFNT fonts (TTF or OTF) to web fonts (WOFF and WOFF2).
    """

    files = get_fonts_list(input_path, allow_extensions=[".otf", ".ttf"])
    if len(files) == 0:
        generic_error_message(f"No valid font files found in {input_path}.")
        return

    output_dir = get_output_dir(fallback_path=input_path, path=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    output_flavors = ["woff", "woff2"]
    if flavor is not None:
        output_flavors = [flavor]

    for file in files:
        try:
            font = Font(file, recalcTimestamp=recalcTimestamp)
            if font.flavor is not None:
                continue
            for flavor in output_flavors:
                font.flavor = flavor
                extension = font.get_real_extension()
                web_font_file = makeOutputFileName(
                    file, extension=extension, outputDir=output_dir, overWrite=overWrite
                )
                font.save(web_font_file, reorderTables=False)
                file_saved_message(web_font_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def ttc_to_sfnt():
    pass


@ttc_to_sfnt.command()
@add_file_or_path_argument()
@add_common_options()
def ttc2sfnt(input_path, outputDir=None, recalcTimestamp=False, overWrite=True):
    """
    Extracts each font from a TTC file, and saves it as a TTF or OTF file.
    """

    if os.path.isfile(input_path):
        files = [input_path]
    elif os.path.isdir(input_path):
        files = [os.path.join(input_path, file) for file in os.listdir(input_path)]
    else:
        generic_error_message(f"Invalid path: {input_path}")
        return

    ttc_files = []
    for file in files:
        try:
            ttc_font = TTCollection(file)
            ttc_files.append(file)
            ttc_font.close()
        except TTLibError:
            pass

    if len(ttc_files) == 0:
        generic_error_message(f"No valid .ttc font files found in {input_path}.")
        return

    output_dir = get_output_dir(fallback_path=input_path, path=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    for ttc_file in ttc_files:
        try:
            ttc_font = TTCollection(ttc_file)
            for font in ttc_font.fonts:
                font.recalcTimestamp = recalcTimestamp
                file_name = font.name_table.getDebugName(6)
                extension = ".otf" if font.sfntVersion == "OTTO" else ".ttf"
                output_file = makeOutputFileName(
                    file_name,
                    extension=extension,
                    outputDir=output_dir,
                    overWrite=overWrite,
                )
                font.save(output_file)
                file_saved_message(output_file)
        except Exception as e:
            generic_error_message(e)


@click.group()
def variable_to_static():
    pass


@variable_to_static.command()
@add_file_or_path_argument()
@click.option(
    "-s",
    "--select-instance",
    is_flag=True,
    default=False,
    help="""
              By default, the script exports all named instances. Use this option to select custom axis values
              for a single instance.
              """,
)
@click.option(
    "--no-cleanup",
    "cleanup",
    is_flag=True,
    default=True,
    help="""
              By default, STAT table is dropped and axis nameIDs are deleted from name table. Use --no-cleanup to keep
              STAT table and prevent axis nameIDs to be deleted from name table.""",
)
@click.option(
    "--update-name-table",
    is_flag=True,
    default=False,
    help="""
              Tries to update the instantiated font's `name` table. Input font must have a STAT table with Axis Value
              Tables.
              """,
)
@add_common_options()
def var2static(
    input_path,
    select_instance=False,
    cleanup=True,
    update_name_table=False,
    outputDir=None,
    recalcTimestamp=False,
    overWrite=True,
):
    """
    Exports static instances from variable fonts.
    """

    files = get_fonts_list(input_path, allow_static=False, allow_cff=False)
    if len(files) == 0:
        generic_error_message(f"No valid font files found in {input_path}")
        return

    output_dir = get_output_dir(fallback_path=input_path, path=outputDir)
    dir_ok, error_message = check_output_dir(output_dir)
    if dir_ok is False:
        generic_error_message(error_message)
        return

    start_time = time.time()
    for file in files:
        print()
        generic_info_message(f"Converting file {os.path.basename(file)}")
        try:
            variable_font = Font(file, recalcTimestamp=recalcTimestamp)
            axes = variable_font.get_axes()
            instances = variable_font.get_instances()

            update_this_font_name_table = update_name_table

            if select_instance:
                selected_coordinates = select_instance_coordinates(axes)
                is_named_instance = selected_coordinates in [
                    i.coordinates for i in instances
                ]
                if not is_named_instance:
                    # Set update_name_table value to False because we won't find this Axis Value in the STAT table.
                    update_this_font_name_table = False
                    selected_instance = NamedInstance()
                    selected_instance.coordinates = selected_coordinates
                else:
                    # In case there are several instances with the same coordinates, return only the first one.
                    #
                    # From https://learn.microsoft.com/en-us/typography/opentype/spec/fvar#instancerecord:
                    #
                    # All the instance records in a font should have distinct coordinates and distinct
                    # subfamilyNameID and postScriptName ID values. If two or more records share the same coordinates,
                    # the same nameID values or the same postScriptNameID values, then all but the first can be ignored.
                    selected_instance = [
                        i for i in instances if i.coordinates == selected_coordinates
                    ][0]

                instances = [selected_instance]

            if len(instances) == 0:
                generic_error_message("No instances found")
                return

            name_ids_to_delete = []
            if cleanup:
                name_ids_to_delete = variable_font.get_var_name_ids_to_delete()

            instance_count = 0

            # Cannot update name table if there is no STAT table.
            if "STAT" not in variable_font:
                update_this_font_name_table = False
                generic_warning_message(
                    "Cannot update name table if there is no STAT table."
                )

            # Cannot update name table if there are no STAT Axis Values.
            if update_this_font_name_table:
                if not hasattr(variable_font["STAT"], "AxisValueArray"):
                    update_this_font_name_table = False
                    generic_warning_message(
                        "Cannot update name table if there are no STAT Axis Values."
                    )

            for instance in instances:
                t = time.time()
                instance_count += 1

                print()
                generic_info_message(
                    f"Exporting instance {instance_count} of {len(instances)}"
                )
                static_font: Font = instantiateVariableFont(
                    varfont=variable_font,
                    axisLimits=instance.coordinates,
                    inplace=False,
                    optimize=True,
                    overlap=OverlapMode.REMOVE_AND_IGNORE_ERRORS,
                    updateFontNames=update_this_font_name_table,
                )

                if cleanup:
                    static_font.name_table.del_names(name_ids=name_ids_to_delete)
                    if "STAT" in static_font:
                        del static_font["STAT"]
                    static_font.reorder_ui_name_ids()

                static_font_file_name = sanitize_filename(
                    variable_font.get_static_instance_file_name(instance)
                )
                static_font_ext = static_font.get_real_extension()
                output_file = makeOutputFileName(
                    static_font_file_name,
                    outputDir=output_dir,
                    extension=static_font_ext,
                    overWrite=overWrite,
                )

                static_font.save(output_file)
                generic_info_message(f"Done in {round(time.time() - t, 3)} seconds")
                file_saved_message(output_file)

            print()
            generic_info_message(f"Total instances : {len(instances)}")
            generic_info_message(
                f"Elapsed time    : {round(time.time() - start_time)} seconds"
            )

        except Exception as e:
            generic_error_message(e)


cli = click.CommandCollection(sources=[otf_2_ttf, ttf_2_otf, web_to_sfnt, sfnt_to_web, ttc_to_sfnt, variable_to_static])