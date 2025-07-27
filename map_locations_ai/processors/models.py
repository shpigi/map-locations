"""
Data models for the map locations AI processors.

These models define the data structures used throughout the processing pipeline.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ChunkData:
    """Represents a chunk of text for processing."""

    id: str
    text: str
    start_line: int
    end_line: int
    total_lines: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "text": self.text,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "total_lines": self.total_lines,
        }


@dataclass
class LLMResult:
    """Result from an LLM processing call."""

    success: bool
    raw_response: str
    parsed_locations: List[Dict[str, Any]]
    processing_time: float
    processing_time_ms: float
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "success": self.success,
            "raw_response": self.raw_response,
            "parsed_locations": self.parsed_locations,
            "processing_time": self.processing_time,
            "processing_time_ms": self.processing_time_ms,
            "error": self.error,
        }


@dataclass
class ProcessingOptions:
    """Options for configuring pipeline processing."""

    with_urls: bool = False
    deduplicate: bool = False
    trace_enabled: bool = True
    backup_enabled: bool = True
    enrichment_enabled: bool = False


@dataclass
class ProcessingResult:
    """Result from pipeline processing."""

    input_file: str
    total_chunks: int
    total_locations: int
    chunk_files: List[str]
    trace_file: str
    deduplication: Optional[Dict[str, Any]] = None
    url_processing: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None


@dataclass
class TraceEntry:
    """Single trace entry for logging."""

    timestamp: str
    chunk_id: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    errors: List[str]


@dataclass
class RunInfo:
    """Information about a complete processing run."""

    timestamp: str
    input_file: str
    total_chunks: int
    total_locations: int
    config: Dict[str, Any]
