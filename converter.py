#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TeleScan2Coe Converter

Converts TeleScan PE PCIE config space files (.tlscan) to Vivado COE files (.coe).
"""

import sys
import re
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Protocol

__all__ = (
    "FileHandler",
    "XMLFileReader",
    "COEFileWriter",
    "TeleScanConverter",
    "main"
)

class FileHandler(Protocol):
    """Protocol defining file handling operations."""

    def read(self, path: Path) -> str:
        """Read and parse content from a file."""
        ...

    def write(self, path: Path, content: str) -> None:
        """Write processed content to a file."""
        ...

class XMLFileReader:
    """Reads and validates TeleScan XML files."""

    def read(self, path: Path) -> str:
        """Read and validate TeleScan XML file."""
        tree = ET.parse(path)
        bytes_element = tree.find('.//bytes')

        if bytes_element is None or bytes_element.text is None:
            raise ValueError("Invalid XML format: Missing <bytes> element")

        hex_data = bytes_element.text.strip()
        self._validate_hex(hex_data)
        return hex_data

    @staticmethod
    def _validate_hex(data: str) -> None:
        """Validate hexadecimal format and length."""
        if len(data) != 8192:
            raise ValueError(f"Invalid hex length: Expected 8192 characters, got {len(data)}")
        if not re.fullmatch(r'[0-9a-fA-F]+', data):
            raise ValueError("Hex data contains invalid characters")

class COEFileWriter:
    """Handles COE file generation with proper formatting."""

    def write(self, path: Path, content: str) -> None:
        """Write formatted COE content to file."""
        path.write_text(content)

class TeleScanConverter:
    """Main conversion processor with optimized memory handling."""

    def __init__(self, reader: FileHandler, writer: FileHandler) -> None:
        """Initialize converter with file handlers."""
        self.reader = reader
        self.writer = writer

    def convert(self, src_path: Path, dst_path: Path) -> None:
        """Execute conversion from TeleScan to COE format."""
        hex_data = self.reader.read(src_path)
        coe_content = self._generate_coe_content(hex_data, src_path)
        self.writer.write(dst_path, coe_content)

    def _generate_coe_content(self, hex_data: str, src_path: Path) -> str:
        """Generate COE formatted content from hex data."""
        header = self._create_header(src_path)
        body = self._create_body(hex_data)
        return header + body

    @staticmethod
    def _create_header(src_path: Path) -> str:
        """Generate COE file header with metadata."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"; TeleScan to COE Conversion\n"
            f"; Source: {src_path.name}\n"
            f"; Generated: {timestamp}\n\n"
            "memory_initialization_radix=16;\n"
            "memory_initialization_vector=\n"
        )

    @staticmethod
    def _create_body(hex_data: str) -> str:
        """Generate COE data body with optimized processing."""
        return ''.join(TeleScanConverter._chunk_generator(hex_data))

    @staticmethod
    def _chunk_generator(hex_data: str) -> str:
        """Efficiently generate formatted COE chunks."""
        buffer = []
        total_chunks = len(hex_data) // 32

        for idx in range(total_chunks):
            if idx % 16 == 0:
                buffer.append(f"\n; {(idx // 16) * 256:04X}\n")

            start = idx * 32
            chunk = hex_data[start:start+32]
            formatted = TeleScanConverter._format_chunk(chunk, is_last=idx == total_chunks-1)
            buffer.append(formatted)

        return buffer

    @staticmethod
    def _format_chunk(chunk: str, is_last: bool) -> str:
        """Format 32-character hex chunk into COE line."""
        parts = [chunk[i*8:(i+1)*8] for i in range(4)]
        terminator = ';' if is_last else ','
        return f"{','.join(parts)}{terminator}\n"

def main() -> None:
    """Command line interface entry point."""
    if len(sys.argv) < 2:
        print("Usage: TeleScan2Coe <source.tlscan> [<destination.coe>]")
        sys.exit(1)

    src_path = Path(sys.argv[1]).resolve()
    dst_path = Path("~/Desktop/output.coe").expanduser() if len(sys.argv) < 3 else Path(sys.argv[2]).resolve()

    converter = TeleScanConverter(XMLFileReader(), COEFileWriter())
    converter.convert(src_path, dst_path)
    print(f"Successfully converted to {dst_path}")

if __name__ == "__main__":
    main()
