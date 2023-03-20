class LibCrelm:
    def __init__(self, lib):
        self._lib = lib

    def make(self, source: str) -> str:
        self._source_buffer = self._lib.new_char_array(source)
        self._header_buffer = self._lib.new_char_array(len(source) + 1)

        self._lib.make_header(self._source_buffer, self._header_buffer)

        return self._lib.string(self._header_buffer).strip()
