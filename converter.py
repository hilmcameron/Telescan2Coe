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

import sys
import datetime
import xml.etree.ElementTree as ET

from pathlib import Path
from typing import Protocol, List

__all__: tuple[str, ...] = (
    "FileReader",
    "FileWriter",
    "XMLFileReader",
    "COEFileWriter",
    "Converter"
)


class FileReader(Protocol):
    def read(self, path: Path) -> str:
        ...


class FileWriter(Protocol):
    def write(self, path: Path, content: str) -> None:
        ...


class XMLFileReader:
    def read(self, path: Path) -> str:
        tree = ET.parse(path)
        result = tree.find('.//bytes')
        if result is None or result.text is None:
            raise ValueError("Invalid XML format: <bytes> element not found or empty")
        return result.text.strip()


class COEFileWriter:
    def write(self, path: Path, content: str) -> None:
        path.write_text(content)


class Converter:
    def __init__(self, reader: FileReader, writer: FileWriter) -> None:
        self.reader = reader
        self.writer = writer

    def convert(self, src_path: Path, dst_path: Path) -> None:
        bs = self.reader.read(src_path)
        bs = ''.join(bs.split())
        if len(bs) != 8192:
            raise ValueError(f'Expected 8192 character (4096 hex byte) string, got {len(bs):,}!')

        content = self._generate_coe_content(bs, src_path)
        self.writer.write(dst_path, content)

    def _generate_coe_content(self, bs: str, src_path: Path) -> str:
        lines: List[str] = [
            f'\n; Converted to COE from "{src_path}" on {datetime.datetime.now()}\n',
            'memory_initialization_radix=16;\nmemory_initialization_vector=\n'
        ]

        for y in range(16):
            lines.append(f'\n; {(y * 256):04X}\n')
            for x in range(16):
                lines.append(f'{bs[0:8]},{bs[8:16]},{bs[16:24]},{bs[24:32]},\n')
                bs = bs[32:]

        lines.append(';\n')
        return ''.join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python TeleScan2Coe.py <source_file.tlscan> [<destination_file.coe>]')
        return

    src_path = Path(sys.argv[1]).resolve()
    dst_path = Path("~/Desktop/output.coe").expanduser() if len(sys.argv) < 3 else Path(sys.argv[2]).resolve()

    reader = XMLFileReader()
    writer = COEFileWriter()
    converter = Converter(reader, writer)
    converter.convert(src_path, dst_path)


if __name__ == "__main__":
    main()
