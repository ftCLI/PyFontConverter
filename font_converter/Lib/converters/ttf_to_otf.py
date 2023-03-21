import cffsubr
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.cliTools import makeOutputFileName
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.subset import Subsetter

from font_converter.Lib.Font import Font
from font_converter.Lib.click_tools import generic_error_message, generic_warning_message


class TrueTypeToCFF(object):
    def __init__(self, input_file: str, output_file: str, recalc_timestamp=False):
        self.font = Font(input_file, recalcTimestamp=recalc_timestamp)
        self.output_file = output_file

    def run(self, charstrings_source="qu2cu", tolerance=1, purge_glyphs=True, subroutinize=True, overwrite=True):

        if purge_glyphs:
            self.purge_glyphs(font=self.font)

        charstrings = {}

        if charstrings_source == "qu2cu":
            self.font.decomponentize()
            try:
                charstrings = self.get_qu2u_charstrings(tolerance=tolerance, all_cubic=True)
            except NotImplementedError:
                generic_warning_message("all_cubic set to False")
                try:
                    charstrings = self.get_qu2u_charstrings(tolerance=tolerance, all_cubic=False)
                except Exception as e:
                    generic_error_message(f"Failed to get charstring with Qu2CuPen ({e})")
                    return

        if charstrings_source == "t2":
            try:
                charstrings = self.get_t2_charstrings()
            except Exception as e:
                generic_error_message(f"Failed to get charstrings with T2CharStringPen ({e})")
                return

        cff_font_info = self.get_cff_font_info(self.font)
        post_values = self.get_post_values(self.font)

        fb = FontBuilder(font=self.font)
        fb.isTTF = False
        for table in ["glyf", "cvt ", "loca", "fpgm", "prep", "gasp", "LTSH", "hdmx"]:
            if table in fb.font:
                del fb.font[table]

        fb.setupCFF(
            psName=self.font["name"].getDebugName(6),
            charStringsDict=charstrings,
            fontInfo=cff_font_info,
            privateDict={},
        )
        fb.setupDummyDSIG()
        fb.setupMaxp()
        fb.setupPost(**post_values)

        if subroutinize:
            # cffsubr doesn't work with woff/woff2 fonts
            flavor = fb.font.flavor
            if flavor is not None:
                fb.font.flavor = None
            cffsubr.subroutinize(fb.font)
            fb.font.flavor = flavor

        ext = fb.font.get_real_extension()
        suffix = ".otf" if ext in ('.woff', '.woff2') else ""

        self.output_file = makeOutputFileName(
            self.output_file, overWrite=overwrite, extension=ext, suffix=suffix
        )

        fb.save(self.output_file)

    @staticmethod
    def get_cff_font_info(font: Font) -> dict:
        """
        Setup CFF topDict

        :return: A dictionary of the font info.
        """

        font_revision = str(round(font["head"].fontRevision, 3)).split(".")
        major_version = str(font_revision[0])
        minor_version = str(font_revision[1]).ljust(3, "0")

        cff_font_info = dict(
            version=".".join([major_version, str(int(minor_version))]),
            FullName=font["name"].getBestFullName(),
            FamilyName=font["name"].getBestFamilyName(),
            ItalicAngle=font["post"].italicAngle,
            UnderlinePosition=font["post"].underlinePosition,
            UnderlineThickness=font["post"].underlineThickness,
        )

        return cff_font_info

    @staticmethod
    def get_post_values(font: Font) -> dict:
        post_info = dict(
            italicAngle=round(font["post"].italicAngle),
            underlinePosition=font["post"].underlinePosition,
            underlineThickness=font["post"].underlineThickness,
            isFixedPitch=font["post"].isFixedPitch,
            minMemType42=font["post"].minMemType42,
            maxMemType42=font["post"].maxMemType42,
            minMemType1=font["post"].minMemType1,
            maxMemType1=font["post"].maxMemType1,
        )
        return post_info

    @staticmethod
    def purge_glyphs(font: Font):

        glyph_ids_to_remove = []
        for g in [".null", "NULL", "uni0000", "CR", "nonmarkingreturn", "uni000D"]:
            try:
                glyph_ids_to_remove.append(font.getGlyphID(g))
            except KeyError:
                pass

        glyph_ids = [
            i
            for i in font.getReverseGlyphMap().values()
            if i not in glyph_ids_to_remove
        ]
        if len(glyph_ids_to_remove) > 0:
            subsetter = Subsetter()
            subsetter.options.drop_tables = []
            subsetter.options.passthrough_tables = True
            subsetter.options.name_IDs = "*"
            subsetter.options.name_legacy = True
            subsetter.options.name_languages = "*"
            subsetter.options.layout_features = "*"
            subsetter.options.hinting = False
            subsetter.glyph_ids_requested = glyph_ids
            Subsetter.subset(subsetter, font)

    def get_qu2u_charstrings(self, tolerance: float = 1, all_cubic: bool = True):

        charstrings = {}
        glyph_set = self.font.getGlyphSet()

        for k, v in glyph_set.items():
            # Correct contours direction and remove overlaps with pathops
            pathops_path = pathops.Path()
            pathops_pen = pathops_path.getPen(glyphSet=glyph_set)
            try:
                glyph_set[k].draw(pathops_pen)
                pathops_path.simplify()
            except TypeError:
                pass

            t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
            qu2cu_pen = Qu2CuPen(t2_pen, max_err=tolerance, all_cubic=all_cubic, reverse_direction=False)
            pathops_path.draw(qu2cu_pen)

            charstring = t2_pen.getCharString()
            charstrings[k] = charstring

        return charstrings

    def get_t2_charstrings(self) -> dict:
        """
        Get CFF charstrings using T2CharStringPen

        :return: CFF charstrings.
        """
        charstrings = {}
        glyph_set = self.font.getGlyphSet()

        for k, v in glyph_set.items():

            # Draw the glyph with T2CharStringPen and get the charstring
            t2_pen = T2CharStringPen(v.width, glyphSet=glyph_set)
            glyph_set[k].draw(t2_pen)
            charstring = t2_pen.getCharString()
            charstrings[k] = charstring

        return charstrings
