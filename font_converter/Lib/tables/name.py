from fontTools.ttLib.tables._n_a_m_e import (
    table__n_a_m_e,
    _MAC_LANGUAGE_CODES,
    _WINDOWS_LANGUAGE_CODES,
)


class TableName(table__n_a_m_e):

    def filter_namerecords(
        self,
        name_ids=None,
        platform_id=None,
        plat_enc_id=None,
        lang_id=None,
        lang_string=None,
    ):
        """
        It takes a list of name records, and returns a list of name records that match the given criteria

        :param name_ids: A list of name IDs to filter by
        :param platform_id: The platform ID of the name record
        :param plat_enc_id: The platform-specific encoding ID
        :param lang_id: The language ID of the name record
        :param lang_string: The string to search for in the name records
        :return: A list of name records.
        """
        filtered_names = self.names
        if name_ids is not None:
            filtered_names = [
                name for name in filtered_names if name.nameID in name_ids
            ]
        if platform_id is not None:
            filtered_names = [
                name for name in filtered_names if name.platformID == platform_id
            ]
        if plat_enc_id is not None:
            filtered_names = [
                name for name in filtered_names if name.platEncID == plat_enc_id
            ]
        if lang_id is not None:
            filtered_names = [name for name in filtered_names if name.langID == lang_id]
        if lang_string is not None:
            mac_lang_id = _MAC_LANGUAGE_CODES.get(lang_string.lower())
            win_lang_id = _WINDOWS_LANGUAGE_CODES.get(lang_string.lower())
            filtered_names = [
                name
                for name in filtered_names
                if name.langID in (mac_lang_id, win_lang_id)
            ]
        return filtered_names

    def del_names(self, name_ids, platform_id=None, language_string=None) -> None:
        """
        Deletes all name records that match the given name_ids, optionally filtering by platform_id and/or
        language_string.

        :param name_ids: A list of name IDs to delete
        :param platform_id: The platform ID of the name records to delete
        :param language_string: The language of the name records to delete
        """

        names = self.filter_namerecords(
            name_ids=name_ids, platform_id=platform_id, lang_string=language_string
        )

        for name in names:
            self.removeNames(name.nameID, name.platformID, name.platEncID, name.langID)
