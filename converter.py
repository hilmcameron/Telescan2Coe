#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TeleScan2Coe Converter

This script converts a TeleScan PE PCIE config space file (.tlscan) to a Vivado COE file (.coe).

Arguments:
    - Source file path of the .tlscan file.
    - Destination file path for the .coe file.

For more information on the COE file format, visit:
https://docs.xilinx.com/r/en-US/ug896-vivado-ip/Using-a-COE-File
"""

import os
import sys
import datetime
import xml.etree.ElementTree as ET

from typing import Protocol, List, Optional

__all__: tuple[str, ...] = (
    "FileReader",
    "FileWriter",
    "XMLFileReader",
    "COEFileWriter",
    "Converter"
)


class FileReader(Protocol):
    def read(self, path: str) -> str:
        ...


class FileWriter(Protocol):
    def write(self, path: str, content: str) -> None:
        ...


class XMLFileReader:
    def read(self, path: str) -> str:
        tree = ET.parse(path)
        return tree.find('.//bytes').text or ''


class COEFileWriter:
    def write(self, path: str, content: str) -> None:
        with open(path, 'w') as fp:
            fp.write(content)


class Converter:
    def __init__(self, reader: FileReader, writer: FileWriter) -> None:
        self.reader = reader
        self.writer = writer

    def convert(self, src_path: str, dst_path: str) -> None:
        bs = self.reader.read(src_path)
        bs = ''.join(bs.split())
        assert len(bs) == 8192, f'Expected 8192 character (4096 hex byte) string, got {len(bs):,}!'

        content = self._generate_coe_content(bs, src_path)
        self.writer.write(dst_path, content)

    def _generate_coe_content(self, bs: str, src_path: str) -> str:
        lines: List[str] = []
        lines.append(f'\n; Converted to COE from "{src_path}" on {datetime.datetime.now()}\n')
        lines.append('memory_initialization_radix=16;\nmemory_initialization_vector=\n')

        for y in range(16):
            lines.append(f'\n; {(y * 256):04X}\n')
            for x in range(16):
                lines.append(f'{bs[0:8]},{bs[8:16]},{bs[16:24]},{bs[24:32]},\n')
                bs = bs[32:]

        lines.append(';\n')
        return ''.join(lines)


def main() -> None:
    assert len(sys.argv) >= 2, 'Assertion failed -> Missing argument'
    src_path = os.path.normpath(sys.argv[1])
    dst_path = os.path.normpath(os.path.expanduser("~/Desktop") + "/output.coe")

    reader = XMLFileReader()
    writer = COEFileWriter()
    converter = Converter(reader, writer)
    converter.convert(src_path, dst_path)


if __name__ == "__main__":
    main()
