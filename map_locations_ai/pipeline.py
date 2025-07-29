#!/usr/bin/env python3
"""
Map Locations AI - Refactored Pipeline Orchestrator
Clean orchestration layer using modular processor components.
"""

import argparse
import os
import time
from typing import Any, Dict, List, Optional

import yaml
from openai import OpenAI

# Try relative imports first (when run as module)
try:
    from .deduplicator import LocationDeduplicator
    from .processors import (
        ChunkData,
        ConfigManager,
        EnrichmentProcessor,
        FileManager,
        LLMProcessor,
        ProcessingOptions,
        TextProcessor,
        TraceManager,
        YAMLProcessor,
    )
    from .processors.geocoding_service import GeocodingService
    from .processors.location_converter import LocationConverter
    from .processors.url_verifier import URLVerifier
    from .url_processor import URLProcessor
except ImportError:
    # Handle script execution or when run directly
    try:
        from map_locations_ai.deduplicator import LocationDeduplicator
        from map_locations_ai.processors import (
            ChunkData,
            ConfigManager,
            EnrichmentProcessor,
            FileManager,
            LLMProcessor,
            ProcessingOptions,
            TextProcessor,
            TraceManager,
            YAMLProcessor,
        )
        from map_locations_ai.processors.geocoding_service import GeocodingService
        from map_locations_ai.processors.location_converter import LocationConverter
        from map_locations_ai.processors.url_verifier import URLVerifier
        from map_locations_ai.url_processor import URLProcessor
    except ImportError:
        # Add current directory to path for direct execution
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))

        from map_locations_ai.deduplicator import LocationDeduplicator
        from map_locations_ai.processors import (
            ChunkData,
            ConfigManager,
            EnrichmentProcessor,
            FileManager,
            LLMProcessor,
            ProcessingOptions,
            TextProcessor,
            TraceManager,
            YAMLProcessor,
        )
        from map_locations_ai.processors.geocoding_service import GeocodingService
        from map_locations_ai.processors.location_converter import LocationConverter
        from map_locations_ai.processors.url_verifier import URLVerifier
        from map_locations_ai.url_processor import URLProcessor


class LocationExtractionPipeline:
    """Orchestrates location extraction using modular processor components."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the pipeline with refactored components."""
        # Initialize configuration (will be updated with input filename later)
        self.config_manager = ConfigManager(config_path)
        self.input_filename: Optional[str] = None

        # Set up OpenAI client
        api_key = os.getenv("LAVI_OPENAI_KEY")
        if not api_key:
            if os.getenv("CI") or os.getenv("TESTING"):
                self.client = None
                print("⚠️  Running in CI/testing mode without OpenAI API key")
            else:
                raise ValueError("LAVI_OPENAI_KEY environment variable is required")
        else:
            # Create tracked OpenAI client (will use singleton usage tracker)
            try:
                from .processors.llm_processor import TrackedOpenAI
            except ImportError:
                from map_locations_ai.processors.llm_processor import TrackedOpenAI
            self.client = TrackedOpenAI(api_key=api_key)

        # Initialize processors
        processing_config = self.config_manager.get_processing_config()
        self.text_processor = TextProcessor(
            chunk_size=processing_config["chunk_size"],
            overlap_size=processing_config["overlap_size"],
        )

        llm_config = self.config_manager.get_llm_config()
        self.llm_processor = LLMProcessor(
            client=self.client,
            agent_prompt=self.config_manager.get_agent_prompt(),
            model=self.config_manager.get_model_for_step("extraction"),
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"],
            timeout=llm_config["timeout"],
            calling_module="LLMProcessor",
        )

        self.yaml_processor = YAMLProcessor(client=self.client, llm_config=llm_config)

        self.trace_manager = TraceManager(
            trace_dir=self.config_manager.get_trace_dir(),
            config=self.config_manager.get_full_config(),
        )

        self.file_manager = FileManager(
            temp_dir=self.config_manager.get_temp_dir(),
            chunk_prefix=self.config_manager.get_chunk_prefix(),
        )

        # Setup directories
        self.config_manager.setup_directories()

        # Initialize URL processor (only if client is available)
        self.url_processor: Optional[URLProcessor] = None
        if self.client is not None:
            self.url_processor = URLProcessor(
                config=self.config_manager.get_full_config(), client=self.client
            )

        # Initialize enrichment processor (only if client is available)
        self.enrichment_processor: Optional[EnrichmentProcessor] = None
        self.url_verifier: Optional[URLVerifier] = None
        self.geocoding_service: Optional[GeocodingService] = None
        if self.client is not None:
            enrichment_config = self.config_manager.get_enrichment_config()
            self.enrichment_processor = EnrichmentProcessor(
                client=self.client,
                model=self.config_manager.get_model_for_step("enrichment"),
                max_searches_per_location=enrichment_config[
                    "max_searches_per_location"
                ],
                timeout=enrichment_config["timeout"],
                trace_manager=self.trace_manager,
                max_retries=enrichment_config.get("max_retries", 2),
            )

            # Configure rate limiting from config
            rate_limit_config = enrichment_config.get("rate_limiting", {})
            self.enrichment_processor.configure_rate_limiting_from_config(
                rate_limit_config
            )

            # Initialize URL verifier
            self.url_verifier = URLVerifier(timeout=10, max_retries=3)

            # Initialize geocoding service
            self.geocoding_service = GeocodingService(
                timeout=10,
                rate_limit_delay=1.0,
                llm_client=self.client,
                llm_model=self.config_manager.get_model_for_step("geocoding"),
            )

        # Initialize location converter
        self.location_converter = LocationConverter()

        # Memory for locations
        self.locations_memory: List[Dict[str, Any]] = []  # type: ignore

    def process_file(
        self, input_file: str, options: Optional[ProcessingOptions] = None
    ) -> Dict[str, Any]:
        """
        Process a single file and extract locations.

        Args:
            input_file: Path to input text file
            options: Processing options

        Returns:
            Dictionary with processing results
        """
        if options is None:
            options = ProcessingOptions()

        # Update config manager with input filename for dynamic paths
        self.input_filename = os.path.basename(input_file)
        self.config_manager.input_filename = self.input_filename  # type: ignore

        # Re-setup directories with new paths
        self.config_manager.setup_directories()

        # Initialize LLM usage tracker singleton with proper directory
        try:
            from .processors.llm_processor import LLMUsageTracker
        except ImportError:
            from map_locations_ai.processors.llm_processor import LLMUsageTracker
        LLMUsageTracker.initialize(self.config_manager.get_temp_dir())

        # Reinitialize file and trace managers with new paths
        self.file_manager = FileManager(
            temp_dir=self.config_manager.get_temp_dir(),
            chunk_prefix=self.config_manager.get_chunk_prefix(),
        )
        self.trace_manager = TraceManager(
            trace_dir=self.config_manager.get_trace_dir(),
            config=self.config_manager.get_full_config(),
        )

        print("=" * 50)
        print("PROCESSING FILE")
        print("=" * 50)
        print(f"Input file: {input_file}")
        print(f"Options: URLs={options.with_urls}, Dedup={options.deduplicate}")

        # Step 1: Text Processing - Read and chunk file
        print("\n🔍 STEP 1: Text Processing")
        try:
            chunks = self.text_processor.read_file_chunks(input_file)
            print(f"✅ Created {len(chunks)} chunks from input file")
        except Exception as e:
            self.trace_manager.trace_error(
                "text_processing", str(e), {"input_file": input_file}
            )
            raise

        # Step 2: LLM Processing - Extract locations from each chunk
        print("\n🤖 STEP 2: LLM Processing")
        chunk_files = []
        total_locations = 0

        for i, chunk in enumerate(chunks, 1):
            print(f"Processing chunk {i}/{len(chunks)}: {chunk.id}")

            try:
                # Extract locations using LLM
                llm_result = self.llm_processor.call_llm(chunk)

                # Trace the LLM call
                self.trace_manager.trace_llm_call(
                    chunk, llm_result, self.config_manager.get_llm_config()
                )

                if llm_result.success:
                    locations = llm_result.parsed_locations

                    # Add chunk_id to each location for tracking
                    for location in locations:
                        location["chunk_id"] = chunk.id

                    # Save chunk YAML
                    chunk_file = self.file_manager.save_chunk_yaml(chunk, locations)
                    chunk_files.append(chunk_file)

                    # Add to memory
                    self.locations_memory.extend(locations)
                    total_locations += len(locations)

                    print(f"  ✅ Extracted {len(locations)} locations")
                else:
                    print(f"  ❌ Failed: {llm_result.error}")
                    self.trace_manager.trace_error(
                        "llm_processing", str(llm_result.error), {"chunk_id": chunk.id}
                    )

            except Exception as e:
                error_msg = f"Error processing chunk {chunk.id}: {e}"
                print(f"  ❌ {error_msg}")
                self.trace_manager.trace_error(
                    "chunk_processing", error_msg, {"chunk_id": chunk.id}
                )
                continue

        print(f"\n✅ LLM Processing complete: {total_locations} locations extracted")

        # Step 3: URL Processing (if requested)
        if options.with_urls:
            print("\n🌐 STEP 3: URL Processing")
            try:
                url_result = self.process_urls()
                self.trace_manager.trace_url_processing(
                    "url_batch", url_result.get("total_urls", 0), url_result
                )
                print(
                    f"✅ URL processing complete: {url_result.get('processed_urls', 0)} URLs processed"
                )
            except Exception as e:
                self.trace_manager.trace_error("url_processing", str(e))
                print(f"❌ URL processing failed: {e}")

        # Step 4: Enrichment (if requested)
        enrichment_result = None
        if options.enrichment_enabled:
            print("\n🔍 STEP 4: Location Enrichment")
            try:
                enrichment_result = self.enrich_locations()
                print(
                    f"✅ Enrichment complete: {enrichment_result['coordinate_coverage']:.1f}% locations have coordinates"
                )

                # Step 5: URL Verification (if available)
                if self.url_verifier is not None and enrichment_result.get(
                    "enriched_locations"
                ):
                    print("\n🔗 STEP 5: URL Verification")
                    try:
                        verified_locations = self.verify_urls(
                            enrichment_result["enriched_locations"]
                        )
                        verification_stats = (
                            self.url_verifier.get_verification_statistics(
                                verified_locations
                            )
                        )
                        print(
                            f"✅ URL verification complete: {verification_stats['reachable_urls']}/{verification_stats['total_urls']} URLs reachable"
                        )
                        print(
                            f"📊 Enrichment rate: {verification_stats['enrichment_rate']}%"
                        )

                        # Update enrichment result with verified locations
                        enrichment_result["enriched_locations"] = verified_locations
                        enrichment_result["verification_stats"] = verification_stats
                    except Exception as e:
                        self.trace_manager.trace_error("url_verification", str(e))
                        print(f"❌ URL verification error: {e}")
                else:
                    print(
                        "\n⏭️  STEP 5: URL verification skipped (no verifier or no enriched locations)"
                    )

                # Step 6: Geocoding (if available and coordinates are missing)
                if self.geocoding_service is not None and enrichment_result.get(
                    "enriched_locations"
                ):
                    print("\n📍 STEP 6: Geocoding")
                    try:
                        geocoded_locations = self.geocode_locations(
                            enrichment_result["enriched_locations"]
                        )
                        geocoding_stats = (
                            self.geocoding_service.get_geocoding_statistics(
                                geocoded_locations
                            )
                        )
                        print(
                            f"✅ Geocoding complete: {geocoding_stats['geocoded_count']} locations geocoded"
                        )
                        print(
                            f"📊 Coordinate coverage: {geocoding_stats['coordinate_coverage']}%"
                        )

                        # Update enrichment result with geocoded locations
                        enrichment_result["enriched_locations"] = geocoded_locations
                        enrichment_result["geocoding_stats"] = geocoding_stats

                        # Write geocoded locations to trace
                        self.trace_manager.trace_operation(
                            "geocoding_complete",
                            f"Geocoded {len(geocoded_locations)} locations",
                            {
                                "geocoding_stats": geocoding_stats,
                                "locations_count": len(geocoded_locations),
                            },
                        )

                        # Save final geocoded locations to YAML files
                        print("\n💾 Saving final geocoded locations...")
                        try:
                            # Convert to Location model format
                            location_model_locations = (
                                self.location_converter.convert_to_location_model(
                                    geocoded_locations
                                )
                            )

                            # Get conversion statistics
                            conversion_stats = (
                                self.location_converter.get_conversion_statistics(
                                    location_model_locations
                                )
                            )

                            # Create updated stats for enriched file (combine enrichment and geocoding stats)
                            stats = enrichment_result.get("stats", {})
                            updated_stats = stats.copy()
                            updated_stats.update(geocoding_stats)

                            # Save enriched locations to file (overwrite previous version)
                            enriched_file = self.file_manager.save_enriched_yaml(
                                geocoded_locations, updated_stats
                            )

                            # Save Location-compliant data to separate file (overwrite previous version)
                            location_file = self.file_manager.save_location_yaml(
                                location_model_locations, conversion_stats  # type: ignore
                            )

                            # Update locations in memory with final geocoded versions
                            self.locations_memory = location_model_locations  # type: ignore

                            print(f"✅ Final locations saved to YAML files")
                            print(f"   📄 Enriched: {enriched_file}")
                            print(f"   📄 Location-compliant: {location_file}")

                        except Exception as e:
                            self.trace_manager.trace_error("final_save", str(e))
                            print(f"❌ Error saving final locations: {e}")
                    except Exception as e:
                        self.trace_manager.trace_error("geocoding", str(e))
                        print(f"❌ Geocoding error: {e}")
                else:
                    print(
                        "\n⏭️  STEP 6: Geocoding skipped (no service or no enriched locations)"
                    )
            except Exception as e:
                self.trace_manager.trace_error("enrichment", str(e))
                print(f"❌ Enrichment failed: {e}")

        # Step 7: Deduplication (if requested)
        dedup_result = None
        if options.deduplicate:
            step_number = "7" if options.enrichment_enabled else "6"
            print(f"\n🔄 STEP {step_number}: Deduplication")
            try:
                dedup_result = self.deduplicate_locations()
                print(
                    f"✅ Deduplication complete: {dedup_result['deduplication_rate']:.1f}% reduction"
                )
            except Exception as e:
                self.trace_manager.trace_error("deduplication", str(e))
                print(f"❌ Deduplication failed: {e}")

        # Step 8: Save trace log
        step_number = "8" if options.enrichment_enabled else "7"
        print(f"\n📊 STEP {step_number}: Save Results")
        run_info = self.trace_manager.create_run_summary(
            input_file=input_file,
            total_chunks=len(chunks),
            total_locations=len(self.locations_memory),
        )
        trace_file = self.trace_manager.save_trace_log(run_info)

        print(f"✅ Processing complete!")
        print(f"  📁 Chunk files: {len(chunk_files)}")
        print(f"  📍 Total locations: {len(self.locations_memory)}")
        print(f"  📋 Trace file: {os.path.basename(trace_file)}")
        if LLMUsageTracker.get_instance():
            print(f"  📊 LLM usage tracked in: llm_calls.csv")

        return {
            "input_file": input_file,
            "total_chunks": len(chunks),
            "total_locations": len(self.locations_memory),
            "chunk_files": chunk_files,
            "trace_file": trace_file,
            "deduplication": dedup_result,
            "options": options,
        }

    def process_urls(self) -> Dict[str, Any]:
        """Process URLs found in extracted locations."""
        if self.url_processor is None:
            print("⚠️ URL processing not available (no OpenAI client)")
            return {
                "processed_chunks": 0,
                "total_urls": 0,
                "processed_urls": 0,
                "error": "OpenAI client required for URL processing",
            }

        # Get all chunk files
        chunk_files = self.file_manager.list_chunk_files()
        processed_count = 0
        total_urls = 0

        for chunk_file in chunk_files:
            if self.url_processor.process_url_entries(os.path.basename(chunk_file)):
                processed_count += 1
            # Count URLs in this chunk
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_data = yaml.safe_load(f)
                url_entries = [
                    loc for loc in chunk_data["locations"] if loc.get("is_url", False)
                ]
                total_urls += len(url_entries)

        return {
            "processed_chunks": processed_count,
            "total_urls": total_urls,
            "processed_urls": total_urls,
        }

    def verify_urls(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify URLs in locations and enrich with content from reachable URLs."""
        if self.url_verifier is None:
            print("⚠️ URL verification not available (no verifier)")
            return locations

        print(f"🔗 Verifying URLs for {len(locations)} locations...")
        return self.url_verifier.verify_and_enrich_urls(locations)

    def geocode_locations(
        self, locations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Geocode locations that are missing coordinates."""
        if self.geocoding_service is None:
            print("⚠️ Geocoding not available (no service)")
            return locations

        print(f"📍 Geocoding {len(locations)} locations...")
        return self.geocoding_service.geocode_locations(locations)

    def enrich_locations(self) -> Dict[str, Any]:
        """Enrich all locations with comprehensive data."""
        if not self.locations_memory:
            return {
                "total_locations": 0,
                "enriched_locations": 0,
                "coordinate_coverage": 0,
                "website_coverage": 0,
                "hours_coverage": 0,
                "stats": {},
            }

        if self.enrichment_processor is None:
            print("⚠️ Enrichment not available (no OpenAI client)")
            return self._create_minimal_enrichment_result()

        print(f"🔍 Enriching {len(self.locations_memory)} locations...")

        # Get enrichment configuration
        enrichment_config = self.config_manager.get_enrichment_config()

        # Check if enrichment is enabled
        if not enrichment_config.get("enabled", True):
            print("⚠️ Enrichment is disabled in configuration")
            return self._create_minimal_enrichment_result()

        # Enrich locations using the processor
        enriched_locations = self.enrichment_processor.enrich_locations(
            self.locations_memory
        )

        # Get enrichment statistics
        stats = self.enrichment_processor.get_enrichment_statistics(enriched_locations)

        # Get retry statistics
        retry_stats = self.enrichment_processor.get_retry_statistics()

        # Report retry statistics if there were any retries
        if retry_stats["total_retry_attempts"] > 0:
            print(f"\n📊 Enrichment Retry Summary:")
            print(
                f"   🔄 {retry_stats['locations_with_retries']}/{retry_stats['total_locations_processed']} locations required retries"
            )
            print(
                f"   📈 {retry_stats['successful_retries']}/{retry_stats['total_retry_attempts']} retry attempts succeeded"
            )
            if retry_stats["successful_retries"] > 0:
                success_rate = (
                    retry_stats["successful_retries"]
                    / retry_stats["total_retry_attempts"]
                ) * 100
                print(f"   📊 Overall retry success rate: {success_rate:.1f}%")

        # Trace enrichment process
        self.trace_manager.trace_operation(
            "enrichment_complete",
            f"Enriched {len(enriched_locations)} locations",
            {
                "enrichment_stats": stats,
                "retry_stats": retry_stats,
                "locations_count": len(enriched_locations),
                "coordinate_coverage": stats["coordinate_coverage"],
                "website_coverage": stats["website_coverage"],
                "hours_coverage": stats["hours_coverage"],
            },
        )

        # Convert to Location model format
        location_model_locations = self.location_converter.convert_to_location_model(
            enriched_locations
        )

        # Get conversion statistics
        conversion_stats = self.location_converter.get_conversion_statistics(
            location_model_locations
        )

        # Save enriched locations to file (intermediate version)
        enriched_file = self.file_manager.save_enriched_yaml(enriched_locations, stats)

        # Save Location-compliant data to separate file
        location_file = self.file_manager.save_location_yaml(
            location_model_locations, conversion_stats  # type: ignore
        )

        # Update locations in memory with Location-compliant versions
        self.locations_memory = location_model_locations  # type: ignore

        # Trace intermediate file saves
        self.trace_manager.trace_operation(
            "intermediate_enrichment_save",
            f"Saved intermediate enriched locations to {enriched_file}",
            {
                "enriched_file": enriched_file,
                "location_file": location_file,
                "locations_count": len(enriched_locations),
            },
        )

        # Trace location conversion
        self.trace_manager.trace_operation(
            "location_conversion_complete",
            f"Converted {len(location_model_locations)} locations to Location model",
            {
                "conversion_stats": conversion_stats,
                "location_yaml_path": location_file,
                "locations_count": len(location_model_locations),
                "validation_rate": conversion_stats["validation_rate"],
                "coordinate_coverage": conversion_stats["coordinate_coverage"],
            },
        )

        return {
            "total_locations": len(enriched_locations),
            "enriched_locations": enriched_locations,  # Return the actual list, not the count
            "coordinate_coverage": stats["coordinate_coverage"],
            "website_coverage": stats["website_coverage"],
            "hours_coverage": stats["hours_coverage"],
            "stats": stats,
            "api_statistics": stats.get("api_statistics", {}),
        }

    def configure_enrichment_rate_limiting(self, min_request_interval: float = 1.0):
        """
        Configure rate limiting for the enrichment processor.

        Args:
            min_request_interval: Minimum seconds between API requests (default: 1.0)
        """
        if self.enrichment_processor is not None:
            self.enrichment_processor.configure_rate_limiting(min_request_interval)
            print(
                f"⚙️  Enrichment rate limiting configured: {min_request_interval}s between requests"
            )
        else:
            print("⚠️  Enrichment processor not available")

    def _create_minimal_enrichment_result(self) -> Dict[str, Any]:
        """Create result when enrichment is not available or disabled."""
        return {
            "total_locations": len(self.locations_memory),
            "enriched_locations": [],
            "coordinate_coverage": 0,
            "website_coverage": 0,
            "hours_coverage": 0,
            "stats": {"status": "no_enrichment_data_available"},
        }

    def deduplicate_locations(self) -> Dict[str, Any]:
        """Deduplicate all locations across chunks."""
        if not self.locations_memory:
            return {
                "total_locations": 0,
                "deduplicated_locations": 0,
                "deduplication_rate": 0,
            }

        # Initialize deduplicator
        dedup_config = self.config_manager.get_deduplication_config()
        deduplicator = LocationDeduplicator(
            config=dedup_config,
            llm_client=self.client,
            llm_model=self.config_manager.get_model_for_step("deduplication"),
        )

        # Perform deduplication
        deduplicated_locations = deduplicator.deduplicate_locations(
            self.locations_memory
        )
        stats = deduplicator.get_stats()

        # Save results
        dedup_file = self.file_manager.save_deduplicated_yaml(
            deduplicated_locations, stats
        )
        merge_report_file = self.file_manager.save_merge_report(stats)

        # Trace deduplication
        self.trace_manager.trace_deduplication(
            len(self.locations_memory), len(deduplicated_locations), stats
        )

        reduction_rate = (
            100 * stats["duplicates_found"] / stats["processed"]
            if stats["processed"] > 0
            else 0
        )

        return {
            "total_locations": len(self.locations_memory),
            "deduplicated_locations": len(deduplicated_locations),
            "duplicates_removed": stats["duplicates_found"],
            "deduplication_rate": reduction_rate,
            "output_file": dedup_file,
            "merge_report_file": merge_report_file,
            "stats": stats,
        }

    def restore_chunks_from_backup(self) -> Dict[str, Any]:
        """Restore chunk files from backup."""
        return self.file_manager.restore_chunks_from_backup()

    def get_summary(self) -> Dict[str, Any]:
        """Get pipeline configuration summary."""
        return {
            "config": self.config_manager.get_config_summary(),
            "locations_in_memory": len(self.locations_memory),
            "trace_stats": self.trace_manager.get_trace_statistics(),
            "file_summary": self.file_manager.get_directory_summary(),
        }


def main() -> int:
    """Main entry point with clean CLI interface."""
    parser = argparse.ArgumentParser(
        description="Extract locations from text files using refactored AI pipeline"
    )
    parser.add_argument("input_file", nargs="?", help="Path to input text file")
    parser.add_argument(
        "--config",
        default="map_locations_ai/config.yaml",
        help="Configuration file path",
    )
    parser.add_argument(
        "--with-urls", action="store_true", help="Process URLs found in locations"
    )
    parser.add_argument(
        "--enrich", action="store_true", help="Enrich locations with comprehensive data"
    )
    parser.add_argument(
        "--deduplicate", action="store_true", help="Deduplicate extracted locations"
    )
    parser.add_argument(
        "--restore-backups", action="store_true", help="Restore chunk files from backup"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show pipeline configuration summary"
    )
    parser.add_argument(
        "--rate-limit-interval",
        type=float,
        default=None,
        help="Minimum seconds between API requests (default: from config)",
    )

    args = parser.parse_args()

    try:
        # Initialize pipeline
        pipeline = LocationExtractionPipeline(args.config)

        # Handle different modes
        if args.summary:
            summary = pipeline.get_summary()
            print("📊 Pipeline Summary:")
            print(f"  Config: {summary['config']['config_file']}")
            print(f"  LLM Model: {summary['config']['llm_model']}")
            print(f"  Locations in Memory: {summary['locations_in_memory']}")
            print(f"  Trace Stats: {summary['trace_stats']['total_traces']} traces")
            print(f"  Files: {summary['file_summary']['total_files']} files")
            return 0

        if args.restore_backups:
            if args.input_file:
                print("⚠️  Ignoring input file when --restore-backups is used")
            result = pipeline.restore_chunks_from_backup()
            print(
                f"✅ Restored {result['restored_chunks']}/{result['total_chunks']} chunks"
            )
            return 0

        # Require input file for processing
        if not args.input_file:
            parser.error(
                "Input file is required (unless using --restore-backups or --summary)"
            )

        # Set processing options
        options = ProcessingOptions(
            with_urls=args.with_urls,
            enrichment_enabled=args.enrich,
            deduplicate=args.deduplicate,
            trace_enabled=True,
            backup_enabled=True,
        )

        # Configure rate limiting if specified
        if args.rate_limit_interval is not None:
            pipeline.configure_enrichment_rate_limiting(args.rate_limit_interval)

        # Process the file
        start_time = time.time()
        result = pipeline.process_file(args.input_file, options)
        processing_time = time.time() - start_time

        # Show final summary
        print(f"\n🎉 Processing completed successfully in {processing_time:.1f}s")
        print(f"  📍 Extracted {result['total_locations']} locations")
        print(f"  📁 Generated {len(result['chunk_files'])} chunk files")
        if result["deduplication"]:
            print(
                f"  🔄 Deduplication: {result['deduplication']['deduplication_rate']:.1f}% reduction"
            )

        return 0

    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
