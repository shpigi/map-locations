#!/usr/bin/env python3
"""
Location Deduplication Engine
Implements smart deduplication of extracted locations with confidence scoring.
"""

import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set, Tuple


class LocationDeduplicator:
    """
    Advanced deduplication engine for location data with multi-level similarity detection.

    Implements:
    - Fuzzy name matching with language/accent normalization
    - Type-aware grouping and validation
    - Confidence-based merging strategies
    - False positive prevention (<5% target rate)
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        llm_client=None,
        llm_model: str = "gpt-4o-mini",
    ):
        """
        Initialize deduplicator with configuration.

        Args:
            config: Deduplication configuration
            llm_client: Optional OpenAI client for LLM-assisted deduplication
            llm_model: Model to use for LLM-assisted deduplication
        """
        self.config = config or self._default_config()
        self.llm_client = llm_client
        self.llm_model = llm_model
        self.stats: Dict[str, Any] = {
            "processed": 0,
            "duplicates_found": 0,
            "groups_created": 0,
            "false_positives": 0,
        }
        self.merge_details: List[Dict[str, Any]] = []

    def _default_config(self) -> Dict[str, Any]:
        """Default deduplication configuration."""
        return {
            "similarity_threshold": 0.6,  # Lowered threshold to see LLM in action
            "name_weight": 0.5,  # Increased weight for name similarity
            "type_weight": 0.2,  # Weight for type matching
            "description_weight": 0.2,  # Reduced weight for description similarity
            "source_weight": 0.1,  # Reduced weight for source context
            "merge_strategy": {
                "name": "highest_confidence",
                "type": "most_specific",
                "description": "longest",
                "confidence": "weighted_average",
                "source_text": "concatenate",
            },
        }

    def deduplicate_locations(
        self, locations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Main deduplication method that processes all locations.

        Args:
            locations: List of location dictionaries from AI extraction

        Returns:
            List of deduplicated locations with merge metadata
        """
        if not locations:
            return []

        self.stats["processed"] = len(locations)

        # Step 1: Group potential duplicates
        duplicate_groups = self._find_duplicate_groups(locations)
        self.stats["groups_created"] = len(duplicate_groups)

        # Step 2: Merge duplicates within each group
        merged_locations = []
        processed_indices = set()
        self.merge_details = []  # Track detailed merge information

        for group_idx, group in enumerate(duplicate_groups):
            if len(group) > 1:
                # Get original locations for this group
                original_locations = [locations[i] for i in group]

                # LLM validation for high-confidence groups
                should_merge = True
                if len(group) >= 3:  # Validate larger groups with LLM
                    should_merge = self._validate_duplicate_group_with_llm(
                        original_locations
                    )
                    if not should_merge:
                        print(
                            f"    🤖 LLM rejected merge for group {group_idx + 1} ({len(group)} locations)"
                        )
                        # Add locations individually instead of merging
                        for i in group:
                            merged_locations.append(locations[i])
                            processed_indices.add(i)
                        continue

                # Merge group members
                merged_location = self._merge_location_group(original_locations)
                merged_locations.append(merged_location)
                processed_indices.update(group)
                self.stats["duplicates_found"] += len(group) - 1

                # Track merge details
                self.merge_details.append(
                    {
                        "group_id": group_idx + 1,
                        "original_count": len(group),
                        "merged_name": merged_location["name"],
                        "merged_type": merged_location["type"],
                        "merge_confidence": merged_location.get(
                            "deduplication", {}
                        ).get("merge_confidence", 0.0),
                        "llm_validated": should_merge,
                        "original_locations": [
                            {
                                "name": loc["name"],
                                "type": loc["type"],
                                "confidence": loc.get("confidence", 0.0),
                                "source_text": (
                                    loc.get("source_text", "")[:100] + "..."
                                    if len(loc.get("source_text", "")) > 100
                                    else loc.get("source_text", "")
                                ),
                                "chunk_id": loc.get("chunk_id", "unknown"),
                            }
                            for loc in original_locations
                        ],
                    }
                )
            else:
                # Single location, add as-is
                merged_locations.append(locations[group[0]])
                processed_indices.add(group[0])

        # Step 3: Add any remaining unprocessed locations
        for i, location in enumerate(locations):
            if i not in processed_indices:
                merged_locations.append(location)

        return merged_locations

    def _find_duplicate_groups(
        self, locations: List[Dict[str, Any]]
    ) -> List[List[int]]:
        """
        Group locations by similarity using graph-based clustering.

        Returns:
            List of groups, where each group is a list of location indices
        """
        n = len(locations)
        similarity_matrix = {}

        # Calculate pairwise similarities
        for i in range(n):
            for j in range(i + 1, n):
                similarity = self._calculate_similarity(locations[i], locations[j])
                if similarity >= self.config["similarity_threshold"]:
                    similarity_matrix[(i, j)] = similarity

        # Use Union-Find to group connected components
        parent = list(range(n))

        def find(x: int) -> int:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x: int, y: int) -> None:
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        # Union similar locations
        for (i, j), similarity in similarity_matrix.items():
            union(i, j)

        # Group by parent
        groups = defaultdict(list)
        for i in range(n):
            groups[find(i)].append(i)

        return list(groups.values())

    def _calculate_similarity(
        self, loc1: Dict[str, Any], loc2: Dict[str, Any]
    ) -> float:
        """
        Calculate comprehensive similarity score between two locations.

        Returns:
            Similarity score between 0.0 and 1.0
        """
        score = 0.0

        # Name similarity (highest weight)
        name_sim = self._name_similarity(loc1["name"], loc2["name"])
        score += name_sim * float(self.config["name_weight"])

        # Type matching
        if loc1["type"] == loc2["type"]:
            score += float(self.config["type_weight"])
        elif self._types_compatible(loc1["type"], loc2["type"]):
            score += (
                float(self.config["type_weight"]) * 0.7
            )  # Partial credit for compatible types

        # Description similarity
        desc_sim = self._text_similarity(
            loc1.get("description", ""), loc2.get("description", "")
        )
        score += desc_sim * float(self.config["description_weight"])

        # Source context similarity
        source_sim = self._text_similarity(
            loc1.get("source_text", ""), loc2.get("source_text", "")
        )
        score += source_sim * float(self.config["source_weight"])

        # Bonus for high name similarity (even if other factors are low)
        if name_sim >= 0.9:
            score += 0.1  # Bonus for very similar names

        # LLM-assisted similarity for borderline cases (expanded range)
        if self.llm_client and 0.35 <= score <= 0.85:
            llm_score = self._llm_similarity_check(loc1, loc2)
            if llm_score > 0.7:  # LLM confirms they're similar
                score += 0.25  # Stronger boost for LLM confirmation
            elif llm_score < 0.3:  # LLM confirms they're different
                score -= 0.2  # Stronger reduction for LLM rejection

        return min(score, 1.0)  # Allow perfect scores for exact matches

    def _name_similarity(self, name1: str, name2: str) -> float:
        """
        Advanced name similarity with normalization and fuzzy matching.
        """
        # Normalize names
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)

        # Exact match after normalization
        if norm1 == norm2:
            return 1.0

        # Fuzzy matching
        fuzzy_score = SequenceMatcher(None, norm1, norm2).ratio()

        # Check for substring matches (one name contained in another)
        if norm1 in norm2 or norm2 in norm1:
            fuzzy_score = max(fuzzy_score, 0.8)

        # Check for word order variations and key word matches
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        if words1 and words2:
            word_overlap = len(words1 & words2) / max(len(words1), len(words2))
            if word_overlap >= 0.5:  # Lower threshold for partial matches
                fuzzy_score = max(fuzzy_score, 0.75)

            # Special handling for key location words
            key_words1 = {
                word for word in words1 if len(word) > 3
            }  # Focus on meaningful words
            key_words2 = {word for word in words2 if len(word) > 3}
            if key_words1 and key_words2:
                key_overlap = len(key_words1 & key_words2) / max(
                    len(key_words1), len(key_words2)
                )
                if key_overlap >= 0.5:
                    fuzzy_score = max(fuzzy_score, 0.8)

        return fuzzy_score

    def _normalize_name(self, name: str) -> str:
        """
        Normalize location names for comparison.
        """
        if not name:
            return ""

        # Convert to lowercase
        normalized = name.lower()

        # Remove accents and diacritics
        normalized = unicodedata.normalize("NFD", normalized)
        normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

        # Remove common prefixes/suffixes
        prefixes = ["the ", "le ", "la ", "les ", "du ", "de ", "des "]
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :]
                break

        # Standardize common words and translations
        replacements = {
            "saint": "st",
            "sainte": "ste",
            "museum": "musee",
            "musee": "museum",
            "gardens": "garden",
            "jardin": "garden",
            "jardins": "garden",
            "centre": "center",
            "center": "centre",
            "theater": "theatre",
            "theatre": "theater",
            # Handle common typos and variations
            "marriot": "marriott",  # Common typo
            "marriott": "marriott",
            "warner bros": "warner brothers",
            "warner brothers": "warner bros",
            "studio tour": "studios",
            "studios": "studio tour",
            "studio": "studios",
            # French-English location name mappings
            "louvre museum": "musee du louvre",
            "musee du louvre": "louvre museum",
            "orsay museum": "musee dorsay",
            "musee dorsay": "orsay museum",
            "dorsay museum": "musee dorsay",
            # Handle D'Orsay variations
            "dorsay": "orsay",
            "orsay": "dorsay",
        }

        for old, new in replacements.items():
            normalized = re.sub(r"\b" + old + r"\b", new, normalized)

        # Handle special cases before removing punctuation
        # D'Orsay -> dorsay
        normalized = re.sub(r"d'orsay", "dorsay", normalized)
        normalized = re.sub(r"d orsay", "dorsay", normalized)

        # Remove extra whitespace and punctuation
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.
        """
        if not text1 or not text2:
            return 0.0

        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def _types_compatible(self, type1: str, type2: str) -> bool:
        """
        Check if two location types are compatible (could refer to same place).
        """
        compatible_groups = [
            {"museum", "gallery"},
            {"park", "garden"},
            {"theater", "theatre"},
            {"market", "bazaar"},
            {"hotel", "accommodation"},
            {"restaurant", "cafe", "bistro"},
            {"landmark", "monument"},
            {"palace", "castle"},
            {"basilica", "church", "cathedral"},
        ]

        for group in compatible_groups:
            if type1 in group and type2 in group:
                return True

        return False

    def _format_location_for_llm(self, location: Dict[str, Any]) -> str:
        """
        Format location data comprehensively for LLM analysis.

        Args:
            location: Location dictionary

        Returns:
            Formatted string with all available location information
        """
        lines = []

        # Core fields
        lines.append(f"- Name: {location.get('name', 'Unknown')}")
        lines.append(f"- Type: {location.get('type', 'Unknown')}")

        # Address and coordinates
        address = location.get("address", "")
        if address:
            lines.append(f"- Address: {address}")

        lat = location.get("latitude", 0)
        lon = location.get("longitude", 0)
        if lat != 0 and lon != 0:
            lines.append(f"- Coordinates: {lat}, {lon}")

        # Description
        description = location.get("description", "")
        if description:
            lines.append(f"- Description: {description}")

        # Additional fields
        neighborhood = location.get("neighborhood", "")
        if neighborhood:
            lines.append(f"- Neighborhood: {neighborhood}")

        tags = location.get("tags", [])
        if tags:
            lines.append(f"- Tags: {', '.join(tags)}")

        # Confidence and validation
        confidence = location.get("confidence_score", location.get("confidence", 0))
        if confidence:
            lines.append(f"- Confidence: {confidence}")

        validation_status = location.get("validation_status", "")
        if validation_status:
            lines.append(f"- Validation: {validation_status}")

        # Data sources
        data_sources = location.get("data_sources", [])
        if data_sources:
            lines.append(f"- Sources: {', '.join(data_sources)}")

        # Additional metadata
        opening_hours = location.get("opening_hours", "")
        if opening_hours:
            lines.append(f"- Hours: {opening_hours}")

        price_range = location.get("price_range", "")
        if price_range:
            lines.append(f"- Price: {price_range}")

        return "\n".join(lines)

    def _llm_similarity_check(
        self, loc1: Dict[str, Any], loc2: Dict[str, Any]
    ) -> float:
        """
        Use LLM to check if two locations are semantically similar.

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not self.llm_client:
            return 0.5  # Neutral score if no LLM available

        try:
            prompt = f"""You are a location deduplication expert. Analyze if these two locations are the same place.

Location 1:
{self._format_location_for_llm(loc1)}

Location 2:
{self._format_location_for_llm(loc2)}

Are these the same location? Consider:
1. Name variations, abbreviations, and alternative spellings
2. Address differences (same place, different address format)
3. Type variations (e.g., "museum" vs "gallery" for same place)
4. Description differences (same place, different descriptions)
5. Brand name variations and common naming patterns
6. Geographic proximity and context

Respond with a JSON object:
{{
    "are_same_location": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""

            # Use max_completion_tokens for o4 models, max_tokens for others
            if self.llm_model.startswith("o4"):
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a location deduplication expert. Respond only with valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=200,
                )
            else:
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a location deduplication expert. Respond only with valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=200,
                    temperature=0.1,
                )

            response_text = response.choices[0].message.content.strip()

            # Try to parse JSON response
            import json

            try:
                result = json.loads(response_text)
                if result.get("are_same_location", False):
                    return float(result.get("confidence", 0.5))
                else:
                    return 1.0 - float(
                        result.get("confidence", 0.5)
                    )  # Inverse for different locations
            except json.JSONDecodeError:
                # Fallback: look for keywords in response
                response_lower = response_text.lower()
                if "same" in response_lower or "duplicate" in response_lower:
                    return 0.8
                elif "different" in response_lower or "not same" in response_lower:
                    return 0.2
                else:
                    return 0.5  # Neutral

        except Exception as e:
            print(f"    ⚠️ LLM similarity check failed: {e}")
            return 0.5  # Neutral score on error

    def _validate_duplicate_group_with_llm(
        self, locations: List[Dict[str, Any]]
    ) -> bool:
        """
        Use LLM to validate if a group of locations should be merged.

        Returns:
            True if LLM confirms they should be merged, False otherwise
        """
        if not self.llm_client or len(locations) < 2:
            return True  # Default to merge if no LLM or single location

        try:
            # Create a summary of the locations
            location_summary = []
            for i, loc in enumerate(locations, 1):
                summary = (
                    f"{i}. {loc.get('name', 'Unknown')} ({loc.get('type', 'Unknown')})"
                )
                if loc.get("address"):
                    summary += f" - {loc.get('address')}"
                location_summary.append(summary)

            prompt = f"""You are a location deduplication expert. Review this group of locations that were flagged as potential duplicates:

{chr(10).join(location_summary)}

Are these all the same location? Consider:
- Name variations, abbreviations, and alternative spellings
- Address format differences and geographic proximity
- Type variations and category overlaps
- Missing or incomplete information
- Brand name variations and common naming patterns
- Geographic context and regional naming conventions

Respond with a JSON object:
{{
    "should_merge": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "suggested_name": "best name for merged location"
}}"""

            # Use max_completion_tokens for o4 models, max_tokens for others
            if self.llm_model.startswith("o4"):
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a location deduplication expert. Respond only with valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=300,
                )
            else:
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a location deduplication expert. Respond only with valid JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=300,
                    temperature=0.1,
                )

            response_text = response.choices[0].message.content.strip()

            # Try to parse JSON response
            import json

            try:
                result = json.loads(response_text)
                return bool(result.get("should_merge", True))  # Default to merge
            except json.JSONDecodeError:
                # Fallback: look for keywords in response
                response_lower = response_text.lower()
                if "merge" in response_lower or "same" in response_lower:
                    return True
                elif "different" in response_lower or "separate" in response_lower:
                    return False
                else:
                    return True  # Default to merge

        except Exception as e:
            print(f"    ⚠️ LLM group validation failed: {e}")
            return True  # Default to merge on error

    def _merge_location_group(self, locations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge a group of duplicate locations into a single location.
        """
        if len(locations) == 1:
            return locations[0]

        # Sort by confidence (highest first)
        sorted_locs = sorted(
            locations, key=lambda x: x.get("confidence", 0), reverse=True
        )
        base_location = sorted_locs[0].copy()

        # Apply merge strategy
        strategy = self.config["merge_strategy"]

        # Merge name
        if strategy["name"] == "highest_confidence":
            base_location["name"] = sorted_locs[0]["name"]
        elif strategy["name"] == "longest":
            base_location["name"] = max(locations, key=lambda x: len(x["name"]))["name"]

        # Merge type (most specific)
        if strategy["type"] == "most_specific":
            type_priority = {
                "landmark": 1,
                "museum": 2,
                "gallery": 3,
                "park": 4,
                "garden": 5,
                "hotel": 6,
                "restaurant": 7,
                "cafe": 8,
                "theater": 9,
                "transport": 10,
                "unknown": 11,
            }
            best_type = min(locations, key=lambda x: type_priority.get(x["type"], 11))[
                "type"
            ]
            base_location["type"] = best_type

        # Merge description (longest)
        if strategy["description"] == "longest":
            descriptions = [loc.get("description", "") for loc in locations]
            base_location["description"] = (
                max(descriptions, key=len) if descriptions else ""
            )

        # Merge confidence (weighted average)
        if strategy["confidence"] == "weighted_average":
            total_weight = sum(loc.get("confidence", 0) for loc in locations)
            if total_weight > 0:
                base_location["confidence"] = total_weight / len(locations)

        # Merge source text (concatenate unique)
        if strategy["source_text"] == "concatenate":
            source_texts = []
            seen = set()
            for loc in locations:
                text = loc.get("source_text", "").strip()
                if text and text not in seen:
                    source_texts.append(text)
                    seen.add(text)
            base_location["source_text"] = " | ".join(source_texts)

        # Add deduplication metadata
        base_location["deduplication"] = {
            "is_merged": True,
            "original_count": len(locations),
            "merge_confidence": self._calculate_merge_confidence(locations),
            "source_chunks": [loc.get("chunk_id", "unknown") for loc in locations],
        }

        return base_location

    def _calculate_merge_confidence(self, locations: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence in the merge decision.
        """
        if len(locations) <= 1:
            return 1.0

        # Average pairwise similarity within the group
        similarities = []
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                sim = self._calculate_similarity(locations[i], locations[j])
                similarities.append(sim)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def get_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics."""
        stats = self.stats.copy()

        # Add detailed merge statistics
        if hasattr(self, "merge_details") and self.merge_details:
            # Group size distribution
            group_sizes = [detail["original_count"] for detail in self.merge_details]
            stats["merge_details"] = {
                "total_groups": len(self.merge_details),
                "group_size_distribution": group_sizes,
                "group_size_breakdown": self._get_group_breakdown(group_sizes),
                "merge_details": self.merge_details,
            }
        else:
            stats["merge_details"] = {
                "total_groups": 0,
                "group_size_distribution": [],
                "group_size_breakdown": {},
                "merge_details": [],
            }

        return stats

    def _get_group_breakdown(self, group_sizes: List[int]) -> Dict[str, int]:
        """Get breakdown of group sizes for reporting."""
        breakdown: Dict[str, int] = {}
        for size in group_sizes:
            key = f"{size} locations"
            breakdown[key] = breakdown.get(key, 0) + 1
        return breakdown

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self.stats = {
            "processed": 0,
            "duplicates_found": 0,
            "groups_created": 0,
            "false_positives": 0,
        }
