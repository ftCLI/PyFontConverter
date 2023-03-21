import os

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.ttLib.ttFont import TTFont, registerCustomTableClass

from font_converter.Lib.tables.name import TableName

registerCustomTableClass("name", "font_converter.Lib.tables.name", "TableName")


class Font(TTFont):
    def __init__(self, file, recalcTimestamp=False):
        super().__init__(file=file, recalcTimestamp=recalcTimestamp)

        self.file = file
        self.name_table: TableName = self["name"]

    @property
    def is_cff(self) -> bool:
        return self.sfntVersion == "OTTO"

    @property
    def is_true_type(self) -> bool:
        return "glyf" in self

    @property
    def is_woff(self) -> bool:
        return self.flavor == "woff"

    @property
    def is_woff2(self) -> bool:
        return self.flavor == "woff2"

    @property
    def is_variable(self) -> bool:
        return "fvar" in self

    @property
    def is_static(self) -> bool:
        return "fvar" not in self

    def get_real_extension(self) -> str:
        if self.flavor is not None:
            return f".{self.flavor}"
        elif self.is_true_type:
            return ".ttf"
        elif self.is_cff:
            return ".otf"

    def decomponentize(self):
        if not self.is_true_type:
            return
        glyph_set = self.getGlyphSet()
        glyf_table = self["glyf"]
        dr_pen = DecomposingRecordingPen(glyph_set)
        tt_pen = TTGlyphPen(None)

        for glyph_name in self.glyphOrder:
            glyph = glyf_table[glyph_name]
            if not glyph.isComposite():
                continue

            dr_pen.value = []
            tt_pen.init()

            glyph.draw(dr_pen, glyf_table)
            dr_pen.replay(tt_pen)

            glyf_table[glyph_name] = tt_pen.glyph()

    # Variable fonts functions


    def get_ui_name_ids(self) -> list:
        """
        Returns a list of all the UI name IDs in the font's GSUB table

        :return: A list of integers.
        """
        ui_name_ids = []
        if "GSUB" not in self.keys():
            return []
        else:
            for record in self["GSUB"].table.FeatureList.FeatureRecord:
                if record.Feature.FeatureParams is not None:
                    ui_name_ids.append(record.Feature.FeatureParams.UINameID)
        return sorted(set(ui_name_ids))

    def reorder_ui_name_ids(self):
        """
        Takes the IDs of the UI names in the name table and reorders them to start at 256
        """

        if "GSUB" not in self:
            return
        ui_name_ids = self.get_ui_name_ids()
        for count, value in enumerate(ui_name_ids, start=256):
            for n in self["name"].names:
                if n.nameID == value:
                    n.nameID = count
            for record in self["GSUB"].table.FeatureList.FeatureRecord:
                if record.Feature.FeatureParams:
                    if record.Feature.FeatureParams.UINameID == value:
                        record.Feature.FeatureParams.UINameID = count

    def get_axes(self) -> list:
        return [axis for axis in self["fvar"].axes if axis.flags == 0]

    def get_instances(self) -> list:
        return [instance for instance in self["fvar"].instances]

    def get_var_name_ids_to_delete(self) -> list:
        name_ids_to_delete = [25]

        if "fvar" in self.keys():
            for axis in self.get_axes():
                name_ids_to_delete.append(axis.axisNameID)
            for instance in self.get_instances():
                if hasattr(instance, "subfamilyNameID"):
                    name_ids_to_delete.append(instance.subfamilyNameID)
                if hasattr(instance, "postscriptNameID"):
                    name_ids_to_delete.append(instance.postscriptNameID)

        if "STAT" in self.keys():
            if hasattr(self["STAT"].table, "DesignAxisRecord"):
                for axis in self["STAT"].table.DesignAxisRecord.Axis:
                    name_ids_to_delete.append(axis.AxisNameID)
            if (
                hasattr(self["STAT"].table, "AxisValueArray")
                and self["STAT"].table.AxisValueArray is not None
            ):
                for axis in self["STAT"].table.AxisValueArray.AxisValue:
                    name_ids_to_delete.append(axis.ValueNameID)

        name_ids_to_delete = [n for n in name_ids_to_delete if n > 24]
        name_ids_to_delete = sorted(list(set(name_ids_to_delete)))

        return name_ids_to_delete

    def get_static_instance_file_name(self, instance: NamedInstance) -> str:
        if hasattr(instance, "postscriptNameID") and instance.postscriptNameID < 65535:
            instance_file_name = self["name"].getDebugName(instance.postscriptNameID)

        else:
            if hasattr(instance, "subfamilyNameID") and instance.subfamilyNameID > 0:
                subfamily_name = self["name"].getDebugName(instance.subfamilyNameID)
            else:
                subfamily_name = "_".join(
                    [f"{k}_{v}" for k, v in instance.coordinates.items()]
                )

            if self["name"].getBestFamilyName() is not None:
                family_name = self["name"].getBestFamilyName()
            else:
                family_name = os.path.splitext(os.path.basename(self.file))[0]

            instance_file_name = f"{family_name}-{subfamily_name}".replace(" ", "")

        return instance_file_name
