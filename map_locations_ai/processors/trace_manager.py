"""
Trace management component for the Map Locations AI pipeline.

Handles comprehensive logging and tracing of all processing operations.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import ChunkData, LLMResult, RunInfo, TraceEntry


class TraceManager:
    """Manages comprehensive logging and tracing."""

    def __init__(self, trace_dir: Path, config: Dict[str, Any]):
        """
        Initialize the trace manager.

        Args:
            trace_dir: Directory to store trace files
            config: Configuration dictionary for context
        """
        self.trace_dir = Path(trace_dir)
        self.config = config
        self.trace_data: List[Dict[str, Any]] = []
        self.trace_file = None

        # Ensure trace directory exists
        self.trace_dir.mkdir(exist_ok=True)

        # Create the trace file for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"run_{timestamp}.json"
        self.trace_file = self.trace_dir / filename

        # Initialize the trace file with run info
        self._initialize_trace_file()

    def _initialize_trace_file(self) -> None:
        """
        Initialize the trace file with basic structure.
        """
        # Write header
        with open(self.trace_file, "w", encoding="utf-8") as f:
            f.write(f"# Trace file: {self.trace_file}\n")
            f.write(f"# Started: {datetime.now(timezone.utc).isoformat()}\n")
            f.write("# Format: timestamp|operation|message|data\n")
            f.write("-" * 80 + "\n")

    def _append_trace_entry(self, trace_entry: Dict[str, Any]) -> None:
        """
        Append a trace entry to the current trace file.

        Args:
            trace_entry: Trace entry to append
        """
        # Format: timestamp|operation|message|data
        timestamp = trace_entry.get("timestamp", datetime.now(timezone.utc).isoformat())
        operation = trace_entry.get("operation", "unknown")
        message = trace_entry.get("message", "")
        chunk_id = trace_entry.get("chunk_id", "")

        # Simplify data to key=value format
        data_parts = []
        if "data" in trace_entry:
            for key, value in trace_entry["data"].items():
                if isinstance(value, (str, int, float, bool)):
                    data_parts.append(f"{key}={value}")
                else:
                    data_parts.append(f"{key}=<complex>")

        data_str = " ".join(data_parts) if data_parts else ""

        # Write simple line format
        with open(self.trace_file, "a", encoding="utf-8") as f:
            line = f"{timestamp}|{operation}|{chunk_id}|{message}|{data_str}\n"
            f.write(line)

    def trace_llm_call(
        self, chunk_data: ChunkData, llm_result: LLMResult, llm_config: Dict[str, Any]
    ) -> None:
        """
        Add LLM call to trace data.

        Args:
            chunk_data: The chunk that was processed
            llm_result: Result from LLM processing
            llm_config: LLM configuration used
        """
        message = f"LLM call for chunk {chunk_data.id}"
        data = {
            "model": llm_config.get("model", "unknown"),
            "success": llm_result.success,
            "locations_count": (
                len(llm_result.parsed_locations) if llm_result.success else 0
            ),
            "processing_time_ms": llm_result.processing_time_ms,
        }
        if llm_result.error:
            data["error"] = str(llm_result.error)[:100]  # Truncate long errors

        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "llm_call",
            "chunk_id": chunk_data.id,
            "message": message,
            "data": data,
        }

        self.trace_data.append(trace_entry)
        self._append_trace_entry(trace_entry)

    def trace_operation(
        self, operation: str, message: str, data: Dict[str, Any]
    ) -> None:
        """
        Add general operation to trace data.

        Args:
            operation: Name of the operation
            message: Human-readable message
            data: Additional data for the operation
        """
        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_id": f"{operation}_process",
            "operation": operation,
            "message": message,
            "data": data,
        }

        self.trace_data.append(trace_entry)
        self._append_trace_entry(trace_entry)

    def save_trace_log(self, run_info: RunInfo) -> str:
        """
        Add final run summary to the trace file.

        Args:
            run_info: Information about the processing run

        Returns:
            Path to the saved trace file
        """
        # Add final summary line
        summary_line = f"{datetime.now(timezone.utc).isoformat()}|summary|run_complete|Processing completed|input_file={run_info.input_file} total_chunks={run_info.total_chunks} total_locations={run_info.total_locations}\n"

        with open(self.trace_file, "a", encoding="utf-8") as f:
            f.write(summary_line)

        return str(self.trace_file)

    def trace_url_processing(
        self, chunk_id: str, url_count: int, processing_result: Dict[str, Any]
    ) -> None:
        """
        Trace URL processing operations.

        Args:
            chunk_id: ID of the chunk being processed
            url_count: Number of URLs found
            processing_result: Result of URL processing
        """
        message = f"URL processing for chunk {chunk_id}"
        data = {
            "url_count": url_count,
            "processed_urls": processing_result.get("processed_urls", 0),
            "total_urls": processing_result.get("total_urls", 0),
        }

        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "url_processing",
            "chunk_id": chunk_id,
            "message": message,
            "data": data,
        }

        self.trace_data.append(trace_entry)
        self._append_trace_entry(trace_entry)

    def trace_deduplication(
        self, original_count: int, deduplicated_count: int, stats: Dict[str, Any]
    ) -> None:
        """
        Trace deduplication operations.

        Args:
            original_count: Number of locations before deduplication
            deduplicated_count: Number of locations after deduplication
            stats: Deduplication statistics
        """
        reduction_percentage = (
            100 * (original_count - deduplicated_count) / original_count
            if original_count > 0
            else 0
        )

        message = f"Deduplication completed: {original_count} -> {deduplicated_count} locations"
        data = {
            "original_count": original_count,
            "deduplicated_count": deduplicated_count,
            "reduction_percentage": round(reduction_percentage, 1),
        }

        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "deduplication",
            "chunk_id": "deduplication",
            "message": message,
            "data": data,
        }

        self.trace_data.append(trace_entry)
        self._append_trace_entry(trace_entry)

    def trace_enrichment(self, location_count: int, stats: Dict[str, Any]) -> None:
        """
        Trace enrichment operations.

        Args:
            location_count: Number of locations processed
            stats: Enrichment statistics
        """
        message = f"Enrichment completed: {location_count} locations processed"
        data = {
            "location_count": location_count,
            "coordinate_coverage": round(stats.get("coordinate_coverage", 0), 1),
            "website_coverage": round(stats.get("website_coverage", 0), 1),
            "hours_coverage": round(stats.get("hours_coverage", 0), 1),
        }

        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "enrichment",
            "chunk_id": "enrichment",
            "message": message,
            "data": data,
        }

        self.trace_data.append(trace_entry)
        self._append_trace_entry(trace_entry)

    def trace_error(
        self, operation: str, error: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Trace error occurrences.

        Args:
            operation: Name of the operation that failed
            error: Error message
            context: Additional context information
        """
        message = f"Error in {operation}: {error}"
        data = {}
        if context:
            for key, value in context.items():
                if isinstance(value, (str, int, float, bool)):
                    data[key] = value

        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": "error",
            "chunk_id": operation,
            "message": message,
            "data": data,
        }

        self.trace_data.append(trace_entry)
        self._append_trace_entry(trace_entry)

    def get_trace_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current trace data.

        Returns:
            Dictionary with trace statistics
        """
        if not self.trace_data:
            return {
                "total_traces": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "operations": {},
            }

        total_traces = len(self.trace_data)
        successful_operations = len([t for t in self.trace_data if not t.get("errors")])
        failed_operations = total_traces - successful_operations

        # Count operations by type
        operations: Dict[str, int] = {}
        for trace in self.trace_data:
            operation = trace.get("operation", "llm_call")
            operations[operation] = operations.get(operation, 0) + 1

        return {
            "total_traces": total_traces,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "operations": operations,
        }

    def clear_trace_data(self) -> None:
        """Clear accumulated trace data."""
        self.trace_data.clear()

    def get_trace_data(self) -> List[Dict[str, Any]]:
        """
        Get copy of current trace data.

        Returns:
            List of trace entries
        """
        return self.trace_data.copy()

    def create_run_summary(
        self, input_file: str, total_chunks: int, total_locations: int
    ) -> RunInfo:
        """
        Create a RunInfo object for the current processing run.

        Args:
            input_file: Path to the input file
            total_chunks: Number of chunks processed
            total_locations: Number of locations extracted

        Returns:
            RunInfo object with run details
        """
        return RunInfo(
            timestamp=datetime.now(timezone.utc).isoformat(),
            input_file=input_file,
            total_chunks=total_chunks,
            total_locations=total_locations,
            config=self.config,
        )
