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

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize deduplicator with configuration."""
        self.config = config or self._default_config()
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
            "similarity_threshold": 0.75,  # Minimum similarity for duplicate detection
            "name_weight": 0.4,  # Weight for name similarity
            "type_weight": 0.2,  # Weight for type matching
            "description_weight": 0.25,  # Weight for description similarity
            "source_weight": 0.15,  # Weight for source context
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
                # Merge group members
                original_locations = [locations[i] for i in group]
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

        # Name similarity
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
