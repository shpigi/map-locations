"""
Text processing component for the Map Locations AI pipeline.

Handles file reading, encoding detection, and text chunking operations.
"""

import os
from pathlib import Path
from typing import List

from .models import ChunkData


class TextProcessor:
    """Handles file reading and text chunking operations."""

    def __init__(self, chunk_size: int = 100, overlap_size: int = 10):
        """
        Initialize the text processor.

        Args:
            chunk_size: Number of lines per chunk
            overlap_size: Number of overlapping lines between chunks
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size

    def read_file_chunks(self, file_path: str) -> List[ChunkData]:
        """
        Read file and split into overlapping chunks.

        Args:
            file_path: Path to the input text file

        Returns:
            List of ChunkData objects representing text chunks

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file encoding is unsupported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")

        lines = self._read_file_with_encoding_detection(file_path)
        return self._create_chunks(lines)

    def _read_file_with_encoding_detection(self, file_path: str) -> List[str]:
        """
        Read file with automatic encoding detection.

        Args:
            file_path: Path to the file to read

        Returns:
            List of lines from the file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.readlines()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.readlines()
            except UnicodeDecodeError as e:
                raise UnicodeDecodeError(
                    "utf-8",
                    b"",
                    0,
                    0,
                    f"Unable to decode file {file_path} with utf-8 or latin-1 encoding",
                ) from e

    def _create_chunks(self, lines: List[str]) -> List[ChunkData]:
        """
        Create overlapping chunks from lines of text.

        Args:
            lines: List of lines from the input file

        Returns:
            List of ChunkData objects
        """
        chunks: List[ChunkData] = []
        total_lines = len(lines)

        if total_lines == 0:
            return chunks

        start = 0
        chunk_id = 1

        while start < total_lines:
            # Calculate end position
            end = min(start + self.chunk_size, total_lines)

            # Extract chunk text
            chunk_lines = lines[start:end]
            chunk_text = "".join(chunk_lines)

            chunk_data = ChunkData(
                id=f"chunk_{chunk_id:03d}",
                text=chunk_text,
                start_line=start + 1,  # 1-indexed
                end_line=end,
                total_lines=len(chunk_lines),
            )

            chunks.append(chunk_data)

            # Move start position (with overlap)
            if end >= total_lines:
                break

            start = end - self.overlap_size
            chunk_id += 1

        return chunks

    def validate_file_format(self, file_path: str) -> bool:
        """
        Validate if file format is supported.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file format is supported, False otherwise
        """
        try:
            path = Path(file_path)

            # Check if file exists
            if not path.exists():
                return False

            # Check if it's a file (not directory)
            if not path.is_file():
                return False

            # Try to read a small portion to check if it's text
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    f.read(1024)  # Try to read first 1KB
                return True
            except UnicodeDecodeError:
                # Try with latin-1
                try:
                    with open(file_path, "r", encoding="latin-1") as f:
                        f.read(1024)
                    return True
                except UnicodeDecodeError:
                    return False

        except Exception:
            return False

    def get_file_info(self, file_path: str) -> dict:
        """
        Get information about the input file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        try:
            lines = self._read_file_with_encoding_detection(file_path)

            return {
                "file_path": file_path,
                "total_lines": len(lines),
                "total_characters": sum(len(line) for line in lines),
                "estimated_chunks": max(1, len(lines) // self.chunk_size),
                "is_valid": True,
            }
        except Exception as e:
            return {"file_path": file_path, "error": str(e), "is_valid": False}
