"""
URL Verification Processor for the Map Locations AI pipeline.

Verifies URLs are reachable and uses their content to enrich location data.
"""

import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class URLVerifier:
    """Verifies URLs and extracts content for location enrichment."""

    def __init__(self, timeout: int = 10, max_retries: int = 3, max_workers: int = 5):
        """
        Initialize the URL verifier.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            max_workers: Maximum number of worker threads
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_workers = max_workers
        self._local = threading.local()
        self._lock = threading.Lock()
        self._progress_counter = 0

    def _get_session(self) -> requests.Session:
        """Get thread-local session."""
        if not hasattr(self._local, "session"):
            self._local.session = self._create_session()
        return self._local.session  # type: ignore[no-any-return]

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set headers to mimic a real browser
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        return session

    def _thread_safe_print(self, message: str) -> None:
        """Thread-safe print function."""
        with self._lock:
            print(message)

    def _update_progress(self, total: int) -> None:
        """Thread-safe progress update."""
        with self._lock:
            self._progress_counter += 1
            print(f"  Progress: {self._progress_counter}/{total} locations processed")

    def verify_and_enrich_urls(
        self, locations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Verify URLs in locations and enrich with content from reachable URLs.

        Args:
            locations: List of location dictionaries

        Returns:
            List of locations with verified URLs and enriched content
        """
        if not locations:
            return []

        self._progress_counter = 0
        total_locations = len(locations)

        self._thread_safe_print(
            f"  Starting URL verification for {total_locations} locations using {self.max_workers} threads"
        )

        # Create a list to store results in the same order as input
        results: List[Optional[Dict[str, Any]]] = [None] * len(locations)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(self._verify_single_location, location): i
                for i, location in enumerate(locations)
            }

            # Collect results as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results[index] = result
                    self._update_progress(total_locations)
                except Exception as e:
                    self._thread_safe_print(f"  Error processing location {index}: {e}")
                    # Keep original location if processing failed
                    results[index] = locations[index]

        self._thread_safe_print(
            f"  ✅ URL verification completed for {total_locations} locations"
        )
        return [result for result in results if result is not None]

    def _verify_single_location(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify URLs for a single location and enrich with content.

        Args:
            location: Location dictionary

        Returns:
            Location with verified URLs and enriched content, unverified URLs marked
        """
        url_fields = ["official_website", "booking_url", "reviews_url"]
        verified_location = location.copy()
        location_name = location.get("name", "Unknown")

        for field in url_fields:
            url = location.get(field, "")
            if url and self._is_valid_url_format(url):
                self._thread_safe_print(
                    f"    Testing {field} for {location_name}: {url}"
                )

                # Test if URL is reachable
                is_reachable, content = self._test_url(url)

                if is_reachable and content:
                    self._thread_safe_print(
                        f"      ✅ URL is reachable for {location_name}"
                    )
                    # Enrich location with content from this URL
                    verified_location = self._enrich_from_url_content(
                        verified_location, field, url, content
                    )
                    # Keep the original URL as verified
                    verified_location[field] = url
                else:
                    self._thread_safe_print(
                        f"      ❌ URL is not reachable for {location_name}"
                    )
                    # Mark URL as unverified but keep it
                    verified_location[field] = f"[UNVERIFIED] {url}"
            elif url:
                self._thread_safe_print(
                    f"    ❌ Invalid URL format for {location_name}: {url}"
                )
                # Mark invalid URL format as unverified but keep it
                verified_location[field] = f"[UNVERIFIED] {url}"

        return verified_location

    def _is_valid_url_format(self, url: str) -> bool:
        """Check if URL has valid format."""
        if not url:
            return False

        # Basic URL validation
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        return bool(url_pattern.match(url))

    def _test_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Test if a URL is reachable and return its content.

        Args:
            url: URL to test

        Returns:
            Tuple of (is_reachable, content)
        """
        try:
            session = self._get_session()
            response = session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                # Extract text content
                soup = BeautifulSoup(response.content, "html.parser")

                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()

                # Get text content
                text = soup.get_text()

                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (
                    phrase.strip() for line in lines for phrase in line.split("  ")
                )
                text = " ".join(chunk for chunk in chunks if chunk)

                return True, text[:2000]  # Limit content length
            else:
                return False, None

        except Exception as e:
            self._thread_safe_print(f"      Error testing URL {url}: {e}")
            return False, None

    def _enrich_from_url_content(
        self, location: Dict[str, Any], url_field: str, url: str, content: str
    ) -> Dict[str, Any]:
        """
        Enrich location with content from a verified URL.

        Args:
            location: Location dictionary
            url_field: Field name of the URL
            url: The verified URL
            content: Content from the URL

        Returns:
            Enriched location dictionary
        """
        enriched = location.copy()

        # Extract useful information from content
        extracted_info = self._extract_location_info_from_content(
            content, location.get("name", "")
        )

        # Update location with extracted information
        if extracted_info.get("description") and not enriched.get("description"):
            enriched["description"] = extracted_info["description"]

        if extracted_info.get("opening_hours") and not enriched.get("opening_hours"):
            enriched["opening_hours"] = extracted_info["opening_hours"]

        if extracted_info.get("price_range") and not enriched.get("price_range"):
            enriched["price_range"] = extracted_info["price_range"]

        if extracted_info.get("accessibility_info") and not enriched.get(
            "accessibility_info"
        ):
            enriched["accessibility_info"] = extracted_info["accessibility_info"]

        # Add URL to data sources
        if "data_sources" not in enriched:
            enriched["data_sources"] = []
        enriched["data_sources"].append(f"verified_{url_field}")

        # Update confidence score
        current_confidence = enriched.get("confidence_score", 0.5)
        enriched["confidence_score"] = min(
            current_confidence + 0.1, 0.95
        )  # Boost confidence

        # Update validation status
        enriched["validation_status"] = "url_verified"

        return enriched

    def _extract_location_info_from_content(
        self, content: str, location_name: str
    ) -> Dict[str, str]:
        """
        Extract location information from web content.

        Args:
            content: Web page content
            location_name: Name of the location

        Returns:
            Dictionary with extracted information
        """
        extracted = {}

        # Look for opening hours patterns
        hours_patterns = [
            r"open.*?(?:daily|monday|tuesday|wednesday|thursday|friday|saturday|sunday).*?(?:am|pm|closed)",
            r"(?:hours|opening).*?(?:daily|monday|tuesday|wednesday|thursday|friday|saturday|sunday).*?(?:am|pm|closed)",
            r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday).*?(?:am|pm|closed)",
        ]

        for pattern in hours_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                extracted["opening_hours"] = match.group(0)[:100]  # Limit length
                break

        # Look for price information
        price_patterns = [
            r"\$\$?\$?\$?",
            r"(?:price|cost).*?(?:free|\$|\£|\€)",
            r"(?:admission|entry).*?(?:free|\$|\£|\€)",
        ]

        for pattern in price_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                extracted["price_range"] = match.group(0)[:50]
                break

        # Look for accessibility information
        accessibility_patterns = [
            r"(?:wheelchair|accessible|disability|ada)",
            r"(?:ramp|elevator|lift)",
        ]

        for pattern in accessibility_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                extracted["accessibility_info"] = "Accessibility features available"
                break

        # Create description if none exists
        if not extracted.get("description"):
            # Extract a relevant sentence containing the location name
            sentences = content.split(".")
            for sentence in sentences:
                if location_name.lower() in sentence.lower() and len(sentence) > 20:
                    extracted["description"] = sentence.strip()[:200]
                    break

        return extracted

    def get_verification_statistics(
        self, locations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about URL verification.

        Args:
            locations: List of verified locations

        Returns:
            Dictionary with verification statistics
        """
        total_locations = len(locations)
        total_urls = 0
        reachable_urls = 0
        unverified_urls = 0
        enriched_locations = 0

        for location in locations:
            url_fields = ["official_website", "booking_url", "reviews_url"]
            location_urls = 0
            location_reachable = 0

            for field in url_fields:
                url = location.get(field, "")
                if url:
                    total_urls += 1
                    location_urls += 1

                    # Check if URL is verified (doesn't start with [UNVERIFIED])
                    if url.startswith("[UNVERIFIED] "):
                        unverified_urls += 1
                    else:
                        reachable_urls += 1
                        location_reachable += 1

            if location_reachable > 0:
                enriched_locations += 1

        return {
            "total_locations": total_locations,
            "total_urls": total_urls,
            "reachable_urls": reachable_urls,
            "unverified_urls": unverified_urls,
            "enriched_locations": enriched_locations,
            "url_success_rate": (
                round(100 * reachable_urls / total_urls, 1) if total_urls > 0 else 0
            ),
            "enrichment_rate": (
                round(100 * enriched_locations / total_locations, 1)
                if total_locations > 0
                else 0
            ),
        }
