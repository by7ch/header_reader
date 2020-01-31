

class OrcParser:
    def __init__(self, content):
        self.content = content
        self.current_index = 0

    def beautify(self, k):
        for i in k:
            print(i, k[i])

    def get_permission(self, k):
        return bin(ord(k))[2:].zfill(3)

    def parse_bytes(self, k):
        result = 0
        shift_amt = 0
        for i in k:
            result |= (i << shift_amt)
            shift_amt += 7
        return result

    def get_text7(self):
        result = ""
        while True:
            if self.content[self.current_index] == 0x00:
                self.current_index += 1
                return result
            result += chr(self.content[self.current_index])
            self.current_index += 1

    def get_word28(self):
        word28 = self.content[self.current_index: self.current_index + 4]
        self.current_index += 4
        return word28

    def get_byte7(self):
        byte7 = self.content[self.current_index: self.current_index + 1]
        self.current_index += 1
        return byte7

    def get_filetype(self):
        return self.get_byte7()

    def get_bool(self):
        return self.get_byte7()

    def parse_symbol(self):
        name = self.get_text7()
        is_define = self.get_bool()
        section, offset = "", ""
        if is_define == b"\x01":
            section = self.get_word28()
            offset = self.get_word28()
        return {
            "name": name,
            "is_define": is_define,
            "section": section,
            "offset": hex(self.parse_bytes(offset)),
        }

    def parse_symbol_table(self):
        num_entries = self.get_word28()
        num_entries = self.parse_bytes(num_entries)
        symbols = []
        for i in range(num_entries):
            # todo: change
            s = self.parse_symbol()
            symbols.append(s)
        return {
            "num_entries": num_entries,
            "symbols": symbols
        }

    def parse_relocation_table(self):
        num_entries = self.get_word28()
        num_entries = self.parse_bytes(num_entries)
        relocations = []

        for i in range(num_entries):
            relocation = self.parse_relocation()
            relocations.append(relocation)
        return {
            "num_entries": num_entries,
            "relocations": relocations
        }

    def parse_relocation(self):
        offset = self.get_word28()
        section = self.get_word28()
        symbol = self.get_text7()
        plus = self.get_word28()
        return {
            "section": section,
            "offset": hex(self.parse_bytes(offset)),
            "symbol": symbol,
            "plus": plus
        }

    def parse_section(self):
        permissions = self.get_byte7()
        offset = self.get_word28()
        name = self.get_text7()
        size = self.get_word28()
        return {
            "permissions": self.get_permission(permissions),
            "offset": hex(self.parse_bytes(offset)),
            "name": name,
            "size": hex(self.parse_bytes(size))
        }

    def parse_section_table(self):
        num_sections = self.get_word28()
        num_sections = self.parse_bytes(num_sections)
        sections = {}
        for section in range(num_sections):
            section = self.parse_section()
            sections[section["name"]] = section
        return sections

    def parse_segment(self):
        name = self.get_text7()
        offset = self.get_word28()
        base = self.get_word28()
        permissions = self.get_byte7()
        segmentType = self.get_byte7()
        # 0b10 for progbits and 0b01 for note
        return {
            "name": name,
            "offset": hex(self.parse_bytes(offset)),
            "base": base,
            "permissions": self.get_permission(permissions),
            "segmentType": segmentType
        }

    def parse_segment_table(self):
        num_entries = self.get_word28()
        num_entries = self.parse_bytes(num_entries)
        segments = []
        for i in range(num_entries):
            s = self.parse_segment()
            segments.append(s)
        return {
            "num_entries": num_entries,
            "segments": segments
        }

    def parse_orcfile_struct(self):
        header = self.get_text7()
        _type = self.get_filetype()
        has_entry_point = self.get_bool()
        entry_point = ""
        if has_entry_point == 0x01:
            entry_point = self.get_word28()

        symbol_table = self.parse_symbol_table()
        relocation_table = self.parse_relocation_table()
        section_table = self.parse_section_table()
        segment_table = self.parse_segment_table()

        return {
            "symbol_table": symbol_table,
            "relocation_table": relocation_table,
            "section_table": section_table,
            "segment_table": segment_table
        }
