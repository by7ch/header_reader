from orcparser import OrcParser

def main():
    with open("a", "rb") as f:
        a = f.read()
    parser = OrcParser(a)
    orc = parser.parse_orcfile_struct()
    parser.beautify(orc["symbol_table"])
    parser.beautify(orc["relocation_table"])
    parser.beautify(orc["section_table"])
    parser.beautify(orc["segment_table"])

if __name__ == '__main__':
    main()
