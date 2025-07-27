"""
File management component for the Map Locations AI pipeline.

Handles all file I/O operations including YAML saving, backup/restore, and report generation.
"""

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .models import ChunkData


class FileManager:
    """Handles all file I/O operations."""

    def __init__(self, temp_dir: Path, chunk_prefix: str = "chunk"):
        """
        Initialize the file manager.

        Args:
            temp_dir: Directory for temporary files
            chunk_prefix: Prefix for chunk file names
        """
        self.temp_dir = Path(temp_dir)
        self.chunk_prefix = chunk_prefix

        # Ensure temp directory exists
        self.temp_dir.mkdir(exist_ok=True)

    def save_chunk_yaml(
        self, chunk_data: ChunkData, locations: List[Dict[str, Any]]
    ) -> str:
        """
        Save locations from a chunk to individual YAML file.

        Args:
            chunk_data: Information about the chunk
            locations: List of locations extracted from the chunk

        Returns:
            Path to the saved file
        """
        filename = f"{self.chunk_prefix}_{chunk_data.id}.yaml"
        filepath = self.temp_dir / filename

        # Prepare YAML data
        yaml_data = {
            "chunk_info": {
                "id": chunk_data.id,
                "start_line": chunk_data.start_line,
                "end_line": chunk_data.end_line,
                "total_lines": chunk_data.total_lines,
            },
            "locations": locations,
        }

        # Save to YAML file
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(
                yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2
            )

        return str(filepath)

    def save_deduplicated_yaml(
        self, locations: List[Dict[str, Any]], stats: Dict[str, Any]
    ) -> str:
        """
        Save deduplicated locations to YAML file.

        Args:
            locations: List of deduplicated locations
            stats: Deduplication statistics

        Returns:
            Path to the saved file
        """
        filename = "deduplicated_locations.yaml"
        filepath = self.temp_dir / filename

        # Prepare YAML data with metadata
        yaml_data = {
            "deduplication_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "original_count": stats["processed"],
                "deduplicated_count": len(locations),
                "duplicates_removed": stats["duplicates_found"],
                "duplicate_groups": stats["groups_created"],
                "reduction_percentage": (
                    round(100 * stats["duplicates_found"] / stats["processed"], 2)
                    if stats["processed"] > 0
                    else 0
                ),
            },
            "locations": locations,
        }

        # Save to YAML file
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(
                yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2
            )

        return str(filepath)

    def save_merge_report(self, stats: Dict[str, Any]) -> str:
        """
        Save detailed merge report with all duplicate groups and their original entries.

        Args:
            stats: Deduplication statistics with merge details

        Returns:
            Path to the saved file
        """
        filename = "deduplication_merge_report.yaml"
        filepath = self.temp_dir / filename

        # Prepare detailed merge report
        merge_report = {
            "merge_report_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_original_locations": stats["processed"],
                "total_duplicate_groups": stats.get("merge_details", {}).get(
                    "total_groups", 0
                ),
                "total_duplicates_found": stats["duplicates_found"],
                "reduction_percentage": (
                    round(100 * stats["duplicates_found"] / stats["processed"], 2)
                    if stats["processed"] > 0
                    else 0
                ),
            },
            "group_size_breakdown": stats.get("merge_details", {}).get(
                "group_size_breakdown", {}
            ),
            "merge_groups": stats.get("merge_details", {}).get("merge_details", []),
        }

        # Save to YAML file
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(
                merge_report, f, default_flow_style=False, allow_unicode=True, indent=2
            )

        return str(filepath)

    def save_enriched_yaml(
        self, locations: List[Dict[str, Any]], stats: Dict[str, Any]
    ) -> str:
        """
        Save enriched locations to YAML file.

        Args:
            locations: List of enriched locations
            stats: Enrichment statistics

        Returns:
            Path to the saved file
        """
        filename = "enriched_locations.yaml"
        filepath = self.temp_dir / filename

        # Prepare YAML data with metadata
        yaml_data = {
            "enrichment_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_locations": stats["total_locations"],
                "coordinate_coverage": f"{stats['coordinate_coverage']}%",
                "website_coverage": f"{stats['website_coverage']}%",
                "hours_coverage": f"{stats['hours_coverage']}%",
                "validation_statuses": stats["validation_statuses"],
            },
            "locations": locations,
        }

        # Save to YAML file
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(
                yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2
            )

        return str(filepath)

    def backup_file(self, filepath: str) -> str:
        """
        Create a backup of the specified file.

        Args:
            filepath: Path to the file to backup

        Returns:
            Path to the backup file

        Raises:
            FileNotFoundError: If the source file doesn't exist
        """
        source_path = Path(filepath)
        if not source_path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {filepath}")

        backup_path = source_path.with_suffix(source_path.suffix + ".backup")
        shutil.copy2(source_path, backup_path)

        print(f"📋 Backup created: {backup_path.name}")
        return str(backup_path)

    def restore_from_backup(self, filepath: str) -> bool:
        """
        Restore a file from its backup.

        Args:
            filepath: Path to the file to restore

        Returns:
            True if restored successfully, False if no backup exists
        """
        source_path = Path(filepath)
        backup_path = source_path.with_suffix(source_path.suffix + ".backup")

        if not backup_path.exists():
            return False

        shutil.copy2(backup_path, source_path)
        print(f"🔄 Restored: {source_path.name}")
        return True

    def restore_chunks_from_backup(self) -> Dict[str, Any]:
        """
        Restore all chunk files from their backups.

        Returns:
            Dictionary with restoration statistics
        """
        restored_chunks = 0
        total_chunks = 0

        for chunk_file in self.temp_dir.glob(f"{self.chunk_prefix}_*.yaml"):
            total_chunks += 1
            backup_file = chunk_file.with_suffix(".yaml.backup")

            if backup_file.exists():
                shutil.copy2(backup_file, chunk_file)
                print(f"  🔄 Restored: {chunk_file.name}")
                restored_chunks += 1
            else:
                print(f"  ⚠️  No backup found: {chunk_file.name}")

        result = {"restored_chunks": restored_chunks, "total_chunks": total_chunks}

        print(f"\n✅ Backup Restoration Complete:")
        print(f"   Restored {restored_chunks}/{total_chunks} chunks")

        return result

    def backup_all_chunks(self) -> Dict[str, Any]:
        """
        Create backups of all chunk files.

        Returns:
            Dictionary with backup statistics
        """
        backed_up_chunks = 0
        total_chunks = 0

        for chunk_file in self.temp_dir.glob(f"{self.chunk_prefix}_*.yaml"):
            total_chunks += 1
            try:
                self.backup_file(str(chunk_file))
                backed_up_chunks += 1
            except Exception as e:
                print(f"  ❌ Failed to backup {chunk_file.name}: {e}")

        result = {"backed_up_chunks": backed_up_chunks, "total_chunks": total_chunks}

        print(f"\n✅ Backup Creation Complete:")
        print(f"   Backed up {backed_up_chunks}/{total_chunks} chunks")

        return result

    def list_chunk_files(self) -> List[str]:
        """
        List all chunk files in the temp directory.

        Returns:
            List of chunk file paths
        """
        chunk_files = []
        for chunk_file in sorted(self.temp_dir.glob(f"{self.chunk_prefix}_*.yaml")):
            chunk_files.append(str(chunk_file))
        return chunk_files

    def list_backup_files(self) -> List[str]:
        """
        List all backup files in the temp directory.

        Returns:
            List of backup file paths
        """
        backup_files = []
        for backup_file in sorted(
            self.temp_dir.glob(f"{self.chunk_prefix}_*.yaml.backup")
        ):
            backup_files.append(str(backup_file))
        return backup_files

    def clean_temp_directory(self, keep_backups: bool = True) -> Dict[str, Any]:
        """
        Clean the temporary directory.

        Args:
            keep_backups: Whether to keep backup files

        Returns:
            Dictionary with cleanup statistics
        """
        deleted_files = 0
        total_files = 0

        # Delete chunk files
        for chunk_file in self.temp_dir.glob(f"{self.chunk_prefix}_*.yaml"):
            total_files += 1
            chunk_file.unlink()
            deleted_files += 1

        # Delete other generated files
        for generated_file in [
            "deduplicated_locations.yaml",
            "deduplication_merge_report.yaml",
        ]:
            file_path = self.temp_dir / generated_file
            if file_path.exists():
                total_files += 1
                file_path.unlink()
                deleted_files += 1

        # Optionally delete backup files
        if not keep_backups:
            for backup_file in self.temp_dir.glob("*.backup"):
                total_files += 1
                backup_file.unlink()
                deleted_files += 1

        result = {
            "deleted_files": deleted_files,
            "total_files": total_files,
            "backups_kept": keep_backups,
        }

        print(f"\n🧹 Cleanup Complete:")
        print(f"   Deleted {deleted_files}/{total_files} files")
        if keep_backups:
            print("   Backup files preserved")

        return result

    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            filepath: Path to the file

        Returns:
            Dictionary with file information
        """
        file_path = Path(filepath)

        if not file_path.exists():
            return {"exists": False, "error": "File not found"}

        try:
            stat = file_path.stat()
            return {
                "exists": True,
                "path": str(file_path),
                "size_bytes": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
            }
        except Exception as e:
            return {"exists": True, "error": str(e)}

    def get_directory_summary(self) -> Dict[str, Any]:
        """
        Get summary of the temp directory contents.

        Returns:
            Dictionary with directory summary
        """
        chunk_files = len(list(self.temp_dir.glob(f"{self.chunk_prefix}_*.yaml")))
        backup_files = len(list(self.temp_dir.glob("*.backup")))
        other_files = len(
            [
                f
                for f in self.temp_dir.iterdir()
                if f.is_file()
                and not f.name.startswith(self.chunk_prefix)
                and not f.name.endswith(".backup")
            ]
        )

        return {
            "temp_directory": str(self.temp_dir),
            "chunk_files": chunk_files,
            "backup_files": backup_files,
            "other_files": other_files,
            "total_files": chunk_files + backup_files + other_files,
        }
