import struct

a = open("a", "rb").read()


def beautify(k):
    for i in k:
        print(i, k[i])


def get_permission(k):
    return bin(ord(k))[2:].zfill(3)


def get_offset(k):
    if k:
        return hex(struct.unpack("I", k)[0])
    else:
        return 0x0


def parse_bytes(k):
    result = 0
    shift_amt = 0
    for i in k:
        result |= (i << shift_amt)
        shift_amt += 7
    return result


def get_text7(current_index: int, content):
    result = ""
    while True:
        if content[current_index] == 0x00:
            return current_index + 1, result
        result += chr(content[current_index])
        current_index += 1


def get_word28(current_index: int, content):
    return current_index + 4, content[current_index: current_index + 4]


def get_filetype(current_index: int, content):
    return current_index + 1, content[current_index: current_index + 1]


def get_byte7(current_index: int, content):
    return current_index + 1, content[current_index: current_index + 1]


def get_bool(current_index: int, content):
    return get_byte7(current_index, content)


def parse_symbol(current_index: int, content):
    current_index, name = get_text7(current_index, content)
    current_index, is_define = get_bool(current_index, content)
    section, offset = "", ""
    if is_define == b"\x01":
        current_index, section = get_word28(current_index, content)
        current_index, offset = get_word28(current_index, content)
    return current_index, {
        "name": name,
        "is_define": is_define,
        "section": section,
        "offset": get_offset(offset),
    }


def parse_symbol_table(current_index: int, content):
    current_index, num_entries = get_word28(current_index, content)
    symbols = []
    for i in range(num_entries[0]):
        # todo: change
        current_index, s = parse_symbol(current_index, content)
        symbols.append(s)
    return current_index, {
        "num_entries": num_entries,
        "symbols": symbols
    }


def parse_relocation_table(current_index: int, content):
    current_index, num_entries = get_word28(current_index, content)
    num_entries = parse_bytes(num_entries)
    relocations = []

    for i in range(num_entries):
        current_index, relocation = parse_relocation(current_index, content)
        relocations.append(relocation)
    return current_index, {
        "num_entries": num_entries,
        "relocations": relocations
    }


def parse_relocation(current_index: int, content):
    current_index, section = get_word28(current_index, content)
    current_index, offset = get_word28(current_index, content)
    current_index, symbol = get_text7(current_index, content)
    current_index, plus = get_word28(current_index, content)
    return current_index, {
        "section": section,
        "offset": get_offset(offset),
        "symbol": symbol,
        "plus": plus
    }


def parse_section_table(current_index: int, content):
    current_index, num_sections = get_word28(current_index, content)
    num_sections = parse_bytes(num_sections)
    sections = {}
    for section in range(num_sections):
        current_index, permissions = get_byte7(current_index, content)
        current_index, offset = get_word28(current_index, content)
        current_index, name = get_text7(current_index, content)
        current_index, size = get_word28(current_index, content)
        sections[name] = {
            "permissions": get_permission(permissions),
            "offset": get_offset(offset),
            "name": name,
            "size": hex(parse_bytes(size))}
    return current_index, sections


def parse_segment(current_index: int, content):
    current_index, name = get_text7(current_index, content)
    current_index, offset = get_word28(current_index, content)
    current_index, base = get_word28(current_index, content)
    current_index, permissions = get_byte7(current_index, content)
    current_index, segmentType = get_byte7(current_index, content)
    # 0b10 for progbits and 0b01 for note
    return current_index, {
        "name": name,
        "offset": get_offset(offset),
        "base": base,
        "permissions": get_permission(permissions),
        "segmentType": segmentType
    }


def parse_segment_table(current_index: int, content):
    current_index, num_entries = get_word28(current_index, content)
    num_entries = parse_bytes(num_entries)
    segments = []
    for i in range(num_entries):
        current_index, s = parse_segment(current_index, content)
        segments.append(s)
    return current_index, {
        "num_entries": num_entries,
        "segments": segments
    }


def parse_orcfile_struct(content):
    current_index = 0
    current_index, header = get_text7(current_index, content)
    current_index, _type = get_filetype(current_index, content)
    current_index, has_entry_point = get_filetype(current_index, content)
    entry_point = ""
    if has_entry_point == 0x01:
        current_index, entry_point = get_word28(current_index, content)
    current_index, symbol_table = parse_symbol_table(current_index, content)

    current_index, relocation_table = parse_relocation_table(
        current_index, content)
    current_index, section_table = parse_section_table(current_index, content)
    current_index, segment_table = parse_segment_table(current_index, content)
    beautify(symbol_table)
    beautify(relocation_table)
    beautify(section_table)
    beautify(segment_table)


parse_orcfile_struct(a)
