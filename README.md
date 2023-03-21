# PyFontConverter

PyFontConverter is a command line tool to convert fonts format.

## Installation

To install in editable mode:
```
git clone https://github.com/ftCLI/font-converter.git
cd font-converter
pip install -e .
```

## Usage

font-converter COMMAND [ARGS]

## Arguments

### INPUT_PATH

All font-converter subcommands process files in the given path. The INPUT_PATH argument can be a single font file
or a folder containing one or more fonts. In case a directory is passed as INPUT_PATH, all fonts stored in it
will be processed, with the exclusion of fonts stored in subdirectories.

## Common options

The `-out, -output-dir`, `--recalc-timestamp` and `--no-overwrite` options can be used in all subcommands, unless
otherwise specified.

### -out, --output-dir

The directory where the converted files are to be saved. If `output_dir` is not specified, files are saved to the
source folder. If `output_dir` doesn't exist, it will be automatically created.

### --recalc-timestamp

By default, original `head.modified` value is kept when a font is saved. Use this switch to set `head.modified`
timestamp  to current time.

### --no-overwrite

By default, converted files are overwritten. Use this switch to save them to a new file (numbers are appended at the end
of file name, so that Times-Bold.otf becomes TimesBold#1.otf).

## Commands

### font-converter ft2wf

Converts SFNT fonts (TTF or OTF) to web fonts (WOFF and WOFF2).

**Usage:**
  
`font-converter ft2wf [OPTIONS] INPUT_PATH`

**Options:**

```
  -f, --flavor [woff|woff2]     By default, the script converts SFNT fonts
                                (TrueType or OpenType) both to woff and woff2
                                flavored web fonts. Use this option to create
                                only woff (--flavor woff) or woff2 (--flavor
                                woff2) files.
  -out, --output-dir DIRECTORY  Specify the directory where output files are
                                to be saved. If output_dir doesn't exist, will
                                be created. If not specified, files are saved
                                to the same folder.
  --recalc-timestamp            Keep the original font 'modified' timestamp
                                (head.modified) or set it to current time. By
                                default, original timestamp is kept.
  --no-overwrite                Overwrite existing output files or save them
                                to a new file (numbers are appended at the end
                                of file name). By default, files are
                                overwritten.
  --help                        Show this message and exit.
```

### font-converter otf2ttf

Converts fonts from CFF to TrueType format.

**Usage:**

`font-converter otf2ttf [OPTIONS] INPUT_PATH`

**Options:**

```
  -out, --output-dir DIRECTORY  Specify the directory where output files are
                                to be saved. If output_dir doesn't exist, will
                                be created. If not specified, files are saved
                                to the same folder.
  --recalc-timestamp            Keep the original font 'modified' timestamp
                                (head.modified) or set it to current time. By
                                default, original timestamp is kept.
  --no-overwrite                Overwrite existing output files or save them
                                to a new file (numbers are appended at the end
                                of file name). By default, files are
                                overwritten.
  --help                        Show this message and exit.
```

### font-converter ttc2sfnt

Extracts each font from a TTC file, and saves it as a TTF or OTF file.

**Usage**

`font-converter ttc2sfnt [OPTIONS] INPUT_PATH`

**Options:**

```
  -out, --output-dir DIRECTORY  Specify the directory where output files are
                                to be saved. If output_dir doesn't exist, will
                                be created. If not specified, files are saved
                                to the same folder.
  --recalc-timestamp            Keep the original font 'modified' timestamp
                                (head.modified) or set it to current time. By
                                default, original timestamp is kept.
  --no-overwrite                Overwrite existing output files or save them
                                to a new file (numbers are appended at the end
                                of file name). By default, files are
                                overwritten.
  --help                        Show this message and exit.
```

### font-converter ttf2otf

Converts fonts from TrueType to CFF format.

**Usage:**

`font-converter ttf2otf [OPTIONS] INPUT_PATH`

**Options**

```
  -t, --tolerance FLOAT RANGE   Conversion tolerance (0-5, default 1). Low
                                tolerance adds more points but keeps shapes.
                                High tolerance adds few points but may change
                                shape.  [0<=x<=5]
  --safe                        Sometimes Qu2CuPen may fail or produce
                                distorted outlines. Most of times, using '--
                                safe' will prevent errors by converting the
                                source TTF font to a temporary OTF built using
                                T2CharstringsPen, and then reconverting it to
                                a temporary TTF font. This last one will be
                                used for TTF to OTF conversion instead of the
                                source TTF file. This is slower and produces
                                slightly bigger files, but is safer.
  --keep-glyphs                 Doesn't remove 'NULL' and 'CR' glyphs from the
                                output font.
  --no-subr                     Turn off subroutinization of converted fonts.
  -out, --output-dir DIRECTORY  Specify the directory where output files are
                                to be saved. If output_dir doesn't exist, will
                                be created. If not specified, files are saved
                                to the same folder.
  --recalc-timestamp            Keep the original font 'modified' timestamp
                                (head.modified) or set it to current time. By
                                default, original timestamp is kept.
  --no-overwrite                Overwrite existing output files or save them
                                to a new file (numbers are appended at the end
                                of file name). By default, files are
                                overwritten.
  --help                        Show this message and exit.
```

### font-converter var2static

Exports static instances from variable fonts.

**Usage:**

`font-converter var2static [OPTIONS] INPUT_PATH`

**Options:**

```
  -s, --select-instance         By default, the script exports all named
                                instances. Use this option to select custom
                                axis values for a single instance.
  --no-cleanup                  By default, STAT table is dropped and axis
                                nameIDs are deleted from name table. Use --no-
                                cleanup to keep STAT table and prevent axis
                                nameIDs to be deleted from name table.
  --update-name-table           Tries to update the instantiated font's `name`
                                table. Input font must have a STAT table with
                                Axis Value Tables.
  -out, --output-dir DIRECTORY  Specify the directory where output files are
                                to be saved. If output_dir doesn't exist, will
                                be created. If not specified, files are saved
                                to the same folder.
  --recalc-timestamp            Keep the original font 'modified' timestamp
                                (head.modified) or set it to current time. By
                                default, original timestamp is kept.
  --no-overwrite                Overwrite existing output files or save them
                                to a new file (numbers are appended at the end
                                of file name). By default, files are
                                overwritten.
  --help                        Show this message and exit.
```

### font-converter wf2ft

Converts web fonts (WOFF and WOFF2) to SFNT fonts (TTF or OTF).

**Usage:**

font-converter wf2ft [OPTIONS] INPUT_PATH

**Options:**

```
  -f, --flavor [woff|woff2]     By default, the script converts both woff and
                                woff2 flavored web fonts to SFNT fonts
                                (TrueType or OpenType). Use this option to
                                convert only woff or woff2 flavored web fonts.
  -d, --delete-source-file      Deletes the source files after conversion.
  -out, --output-dir DIRECTORY  Specify the directory where output files are
                                to be saved. If output_dir doesn't exist, will
                                be created. If not specified, files are saved
                                to the same folder.
  --recalc-timestamp            Keep the original font 'modified' timestamp
                                (head.modified) or set it to current time. By
                                default, original timestamp is kept.
  --no-overwrite                Overwrite existing output files or save them
                                to a new file (numbers are appended at the end
                                of file name). By default, files are
                                overwritten.
  --help                        Show this message and exit.
```
