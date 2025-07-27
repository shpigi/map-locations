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

        # Ensure trace directory exists
        self.trace_dir.mkdir(exist_ok=True)

    def trace_llm_call(
        self, chunk_data: ChunkData, llm_result: LLMResult, llm_config: Dict[str, Any]
    ) -> None:
        """
        Add LLM call to trace data and write to file immediately.

        Args:
            chunk_data: The chunk that was processed
            llm_result: Result from LLM processing
            llm_config: LLM configuration used
        """
        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_id": chunk_data.id,
            "input": {
                "chunk_text": (
                    chunk_data.text[:500] + "..."
                    if len(chunk_data.text) > 500
                    else chunk_data.text
                ),
                "start_line": chunk_data.start_line,
                "end_line": chunk_data.end_line,
                "model": llm_config.get("model", "unknown"),
                "temperature": llm_config.get("temperature", 0.1),
            },
            "output": {
                "success": llm_result.success,
                "raw_response": llm_result.raw_response,
                "parsed_locations": llm_result.parsed_locations,
                "processing_time_ms": llm_result.processing_time_ms,
            },
            "errors": [llm_result.error] if llm_result.error else [],
        }

        self.trace_data.append(trace_entry)

        # Write trace to file immediately
        self._write_trace_entry(trace_entry)

    def _write_trace_entry(self, trace_entry: Dict[str, Any]) -> None:
        """
        Write a single trace entry to file immediately.

        Args:
            trace_entry: Single trace entry to write
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trace_{timestamp}.json"
        filepath = self.trace_dir / filename

        # Create a simple trace entry with just this call
        trace_log = {
            "run_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "single_entry": True,
                "chunk_id": trace_entry["chunk_id"],
            },
            "trace": trace_entry,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trace_log, f, indent=2, ensure_ascii=False)

        print(f"Trace written to: {filepath}")

    def save_trace_log(self, run_info: RunInfo) -> str:
        """
        Save complete trace data to JSON file.

        Args:
            run_info: Information about the processing run

        Returns:
            Path to the saved trace file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"run_{timestamp}.json"
        filepath = self.trace_dir / filename

        trace_log = {
            "run_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "input_file": run_info.input_file,
                "total_chunks": run_info.total_chunks,
                "total_locations": run_info.total_locations,
                "config": run_info.config,
            },
            "traces": self.trace_data,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trace_log, f, indent=2, ensure_ascii=False)

        return str(filepath)

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
        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_id": f"{chunk_id}_url_processing",
            "operation": "url_processing",
            "input": {
                "url_count": url_count,
            },
            "output": processing_result,
            "errors": [],
        }

        self.trace_data.append(trace_entry)
        self._write_trace_entry(trace_entry)

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
        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_id": "deduplication_process",
            "operation": "deduplication",
            "input": {
                "original_count": original_count,
            },
            "output": {
                "deduplicated_count": deduplicated_count,
                "reduction_percentage": (
                    100 * (original_count - deduplicated_count) / original_count
                    if original_count > 0
                    else 0
                ),
                "stats": stats,
            },
            "errors": [],
        }

        self.trace_data.append(trace_entry)
        self._write_trace_entry(trace_entry)

    def trace_enrichment(self, location_count: int, stats: Dict[str, Any]) -> None:
        """
        Trace enrichment operations.

        Args:
            location_count: Number of locations processed
            stats: Enrichment statistics
        """
        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_id": "enrichment_process",
            "operation": "enrichment",
            "input": {
                "location_count": location_count,
            },
            "output": {
                "enriched_count": location_count,
                "coordinate_coverage": stats.get("coordinate_coverage", 0),
                "website_coverage": stats.get("website_coverage", 0),
                "hours_coverage": stats.get("hours_coverage", 0),
                "validation_statuses": stats.get("validation_statuses", {}),
                "stats": stats,
            },
            "errors": [],
        }

        self.trace_data.append(trace_entry)
        self._write_trace_entry(trace_entry)

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
        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_id": f"error_{operation}",
            "operation": operation,
            "input": context or {},
            "output": {},
            "errors": [error],
        }

        self.trace_data.append(trace_entry)
        self._write_trace_entry(trace_entry)

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
