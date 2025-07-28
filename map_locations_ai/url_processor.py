#!/usr/bin/env python3
"""
URL Processor - Extract location information from URLs using LLM
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml
from bs4 import BeautifulSoup
from openai import OpenAI


class URLProcessor:
    """Lean URL processor for extracting location info from web pages."""

    def __init__(self, config: Dict[str, Any], client: OpenAI):
        """Initialize with config and OpenAI client."""
        self.config = config
        self.client = client
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (compatible; LocationBot/1.0)"}
        )

    def process_url_entries(self, chunk_file: Path) -> bool:
        """Process all URL entries in a chunk file."""
        try:
            # Create backup of original file
            backup_file = chunk_file.with_suffix(".yaml.backup")
            if not backup_file.exists():
                import shutil

                shutil.copy2(chunk_file, backup_file)
                print(f"  💾 Created backup: {backup_file.name}")

            # Load chunk data
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_data = yaml.safe_load(f)

            # Find URL entries
            url_entries = [
                loc for loc in chunk_data["locations"] if loc.get("is_url", False)
            ]

            if not url_entries:
                return False

            print(f"📍 Processing {len(url_entries)} URLs in {chunk_file.name}")

            # Process each URL
            processed_locations = []
            for url_entry in url_entries:
                processed = self._process_single_url(url_entry)
                processed_locations.append(processed)
                time.sleep(0.5)  # Aggressive rate limiting

            # Replace URL entries with processed data
            non_url_locations = [
                loc for loc in chunk_data["locations"] if not loc.get("is_url", False)
            ]
            chunk_data["locations"] = non_url_locations + processed_locations

            # Save updated chunk
            with open(chunk_file, "w", encoding="utf-8") as f:
                yaml.dump(chunk_data, f, default_flow_style=False, sort_keys=False)

            print(f"  ✅ Updated: {chunk_file.name}")
            return True

        except Exception as e:
            print(f"❌ Error processing {chunk_file}: {e}")
            # Restore from backup if available
            backup_file = chunk_file.with_suffix(".yaml.backup")
            if backup_file.exists():
                import shutil

                shutil.copy2(backup_file, chunk_file)
                print(f"  🔄 Restored from backup: {backup_file.name}")
            return False

    def _process_single_url(self, url_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single URL entry."""
        url = url_entry["url"]
        print(f"  🔍 Processing: {url}")

        try:
            # Fetch URL content
            content = self._fetch_url_content(url)
            if not content:
                return self._create_failed_entry(
                    url_entry, "Failed to fetch URL content"
                )

            # Extract location info using LLM
            location_info = self._extract_with_llm(url, content)
            if not location_info:
                return self._create_failed_entry(
                    url_entry, "Failed to extract location info"
                )

            # Merge with original entry
            return self._merge_url_data(url_entry, location_info)

        except Exception as e:
            print(f"    ❌ Error: {e}")
            return self._create_failed_entry(url_entry, f"Error: {e}")

    def _fetch_url_content(self, url: str) -> Optional[str]:
        """Fetch and clean HTML content from URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove noise
            for element in soup(
                ["nav", "footer", "header", "aside", "script", "style"]
            ):
                element.decompose()

            # Extract key content
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else ""

            # Get main content (first few paragraphs + headings)
            content_parts = []
            if title_text:
                content_parts.append(f"Title: {title_text}")

            # Get first few headings and paragraphs
            for tag in soup.find_all(["h1", "h2", "h3", "p"])[:10]:
                text = tag.get_text(strip=True)
                if text and len(text) > 20:  # Skip very short text
                    content_parts.append(text)

            content = "\n".join(content_parts)

            # Limit content length (keep it lean for LLM)
            if len(content) > 2000:
                content = content[:2000] + "..."

            return content if content and content.strip() else None

        except Exception as e:
            print(f"    ❌ Fetch error: {e}")
            return None

    def _extract_with_llm(self, url: str, content: str) -> Optional[Dict[str, Any]]:
        """Extract location info using LLM."""
        prompt = f"""Extract location information from this webpage content.

URL: {url}
Content: {content}

Extract:
1. Name of the location/venue/place
2. Brief 1-2 sentence description
3. Type: landmark, museum, park, passage, hotel, restaurant, transport,
   neighborhood, attraction, other
4. Address if mentioned

Return JSON only:
{{"name": "Location Name", "description": "Brief description", "type": "landmark", "address": ""}}

If not a specific location, return: {{"name": null}}"""

        try:
            # Use max_completion_tokens for o4 models, max_tokens for others
            model = self.config["llm"]["model"]
            if model.startswith("o4"):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=500,
                    calling_module="URLProcessor",
                    operation_type="url_extraction",
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=500,
                    calling_module="URLProcessor",
                    operation_type="url_extraction",
                )

            result_text = response.choices[0].message.content
            if result_text is None:
                raise ValueError("Empty response from LLM")
            result_text = result_text.strip()

            # Clean JSON if wrapped in markdown
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()

            result: Dict[str, Any] = json.loads(result_text)

            # Check if it's a valid location
            if not result.get("name"):
                return None

            return result

        except Exception as e:
            print(f"    ❌ LLM error: {e}")
            return None

    def _merge_url_data(
        self, original: Dict[str, Any], extracted: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge extracted data with original URL entry."""
        return {
            "name": extracted.get("name", original["name"]),
            "type": extracted.get("type", "attraction"),
            "description": extracted.get("description", "Location extracted from URL"),
            "source_text": original["source_text"],  # Keep original
            "confidence": 0.7,  # URL processing confidence
            "is_url": True,  # Keep flag
            "url": original["url"],
            "address": extracted.get("address", ""),
            "extraction_method": "llm",
        }

    def _create_failed_entry(
        self, original: Dict[str, Any], error_msg: str
    ) -> Dict[str, Any]:
        """Create entry for failed URL processing."""
        return {
            "name": original["name"],
            "type": "unknown",
            "description": f"Failed to fetch URL content: {error_msg}",
            "source_text": original["source_text"],
            "confidence": 0.2,
            "is_url": True,
            "url": original["url"],
            "address": "",
            "extraction_method": "failed",
        }
