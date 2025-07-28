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
        # Cache for similarity calculations to avoid recomputation
        self._similarity_cache: Dict[Tuple[int, int], float] = {}
        # Track groups that have been processed to avoid infinite loops
        self._processed_groups: Set[Tuple[int, ...]] = set()

    def _default_config(self) -> Dict[str, Any]:
        """Default deduplication configuration."""
        return {
            "similarity_threshold": 0.75,  # Increased for more precision
            "name_weight": 0.35,  # Reduced to balance with new factors
            "type_weight": 0.15,  # Reduced to balance with new factors
            "description_weight": 0.35,  # Increased for better content matching
            "address_weight": 0.10,  # NEW: Weight for address similarity
            "source_weight": 0.05,  # Reduced to balance with new factors
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

        # Reset caches and tracking for new run
        self._similarity_cache.clear()
        self._processed_groups.clear()

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

                        # Try re-clustering with higher threshold
                        if len(group) > 2:  # Only try re-clustering for groups > 2
                            print(
                                f"    🔄 Attempting re-clustering for rejected group..."
                            )
                            reclustered_locations = (
                                self._try_recluster_with_higher_threshold(
                                    original_locations,
                                    self.config["similarity_threshold"],
                                )
                            )

                            # Add re-clustered results (these are already the final locations)
                            for reclustered_loc in reclustered_locations:
                                merged_locations.append(reclustered_loc)

                            # Mark all original indices as processed
                            processed_indices.update(group)
                        else:
                            # For groups of 2, just add locations individually
                            for i in group:
                                merged_locations.append(locations[i])
                                processed_indices.add(i)

                        continue

                # Merge group members (LLM approved or no LLM validation needed)
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
        Calculate similarity between two locations using weighted factors.

        Args:
            loc1: First location dictionary
            loc2: Second location dictionary

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Use cached similarity if available
        loc1_id = id(loc1)
        loc2_id = id(loc2)
        cache_key = (min(loc1_id, loc2_id), max(loc1_id, loc2_id))

        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]

        # Calculate similarity components
        name_sim = self._name_similarity(loc1.get("name", ""), loc2.get("name", ""))
        type_sim = (
            1.0
            if self._types_compatible(loc1.get("type", ""), loc2.get("type", ""))
            else 0.0
        )
        desc_sim = self._text_similarity(
            loc1.get("description", ""), loc2.get("description", "")
        )

        # Address similarity (NEW)
        address_sim = self._address_similarity(
            loc1.get("address", ""), loc2.get("address", "")
        )

        # Source context similarity
        source_sim = self._text_similarity(
            loc1.get("source_text", ""), loc2.get("source_text", "")
        )

        # Geographic distance penalty (NEW)
        geo_penalty = self._geographic_distance_penalty(loc1, loc2)

        # Calculate weighted score
        score = (
            name_sim * float(self.config["name_weight"])
            + type_sim * float(self.config["type_weight"])
            + desc_sim * float(self.config["description_weight"])
            + address_sim * float(self.config["address_weight"])
            + source_sim * float(self.config["source_weight"])
        )

        # Apply geographic penalty
        score -= geo_penalty

        # Apply LLM boost for borderline cases
        if 0.35 <= score <= 0.85:
            llm_boost = self._llm_similarity_check(loc1, loc2)
            score = min(score + llm_boost, 1.0)

        # Cache the result
        final_score = min(max(score, 0.0), 1.0)  # Clamp between 0.0 and 1.0
        self._similarity_cache[cache_key] = final_score

        return final_score

    def _find_least_similar_pair(
        self, locations: List[Dict[str, Any]]
    ) -> Tuple[int, int, float]:
        """
        Find the pair of locations with the lowest similarity.

        Args:
            locations: List of location dictionaries

        Returns:
            Tuple of (index1, index2, similarity_score)
        """
        min_similarity = 1.0
        min_pair = (0, 1)

        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                similarity = self._calculate_similarity(locations[i], locations[j])
                if similarity < min_similarity:
                    min_similarity = similarity
                    min_pair = (i, j)

        return min_pair[0], min_pair[1], min_similarity

    def _split_group_around_pair(
        self, locations: List[Dict[str, Any]], idx1: int, idx2: int
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Split a group of locations around a pair, creating two subgroups.

        Args:
            locations: List of location dictionaries
            idx1: Index of first location in the pair
            idx2: Index of second location in the pair

        Returns:
            Tuple of (group1, group2) where each group contains locations
        """
        # Create two groups based on similarity to each member of the pair
        group1 = [locations[idx1]]
        group2 = [locations[idx2]]

        for i, loc in enumerate(locations):
            if i == idx1 or i == idx2:
                continue

            # Calculate similarity to both members of the pair
            sim_to_1 = self._calculate_similarity(loc, locations[idx1])
            sim_to_2 = self._calculate_similarity(loc, locations[idx2])

            # Assign to the group with higher similarity
            if sim_to_1 > sim_to_2:
                group1.append(loc)
            else:
                group2.append(loc)

        return group1, group2

    def _find_least_similar_location(
        self, locations: List[Dict[str, Any]]
    ) -> Tuple[int, float]:
        """
        Find the location with the lowest average similarity to all others.

        Args:
            locations: List of location dictionaries

        Returns:
            Tuple of (index, average_similarity)
        """
        min_avg_sim = 1.0
        min_idx = 0

        for i in range(len(locations)):
            similarities = []
            for j in range(len(locations)):
                if i != j:
                    sim = self._calculate_similarity(locations[i], locations[j])
                    similarities.append(sim)

            avg_sim = sum(similarities) / len(similarities)
            if avg_sim < min_avg_sim:
                min_avg_sim = avg_sim
                min_idx = i

        return min_idx, min_avg_sim

    def _find_optimal_split_threshold(self, locations: List[Dict[str, Any]]) -> float:
        """
        Find the optimal threshold to split a group by analyzing similarity distribution.

        Args:
            locations: List of location dictionaries

        Returns:
            Optimal threshold for splitting the group
        """
        if len(locations) < 3:
            return 0.98  # Very high threshold for small groups

        # Calculate all pairwise similarities
        similarities = []
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                sim = self._calculate_similarity(locations[i], locations[j])
                similarities.append(sim)

        # Sort similarities in descending order
        similarities.sort(reverse=True)

        # Find the optimal split point
        # Strategy: Look for the biggest drop in similarity
        if len(similarities) >= 2:
            # Find the largest gap between consecutive similarities
            max_gap = 0.0
            optimal_threshold = 0.98  # Default to very high threshold

            for i in range(len(similarities) - 1):
                gap = similarities[i] - similarities[i + 1]
                if gap > max_gap and gap > 0.1:  # Significant gap
                    max_gap = gap
                    # Use the lower similarity as threshold (split after this point)
                    optimal_threshold = similarities[i + 1] + 0.01  # Slightly above

            # If no significant gap found, use a conservative threshold
            if max_gap <= 0.1:
                optimal_threshold = (
                    min(similarities) + 0.05
                )  # Just above the lowest similarity

            return optimal_threshold
        else:
            return 0.98  # Single similarity, use very high threshold

    def _try_recluster_with_higher_threshold(
        self,
        locations: List[Dict[str, Any]],
        original_threshold: float,
        recursion_depth: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Try re-clustering a group with a higher threshold when initial merge is rejected.
        Uses deterministic threshold finding based on similarity distribution.

        Args:
            locations: List of location dictionaries
            original_threshold: Original similarity threshold
            recursion_depth: Current recursion depth (max 2)

        Returns:
            List of deduplicated locations (either merged or individual)
        """
        # Base cases
        if len(locations) <= 2 or recursion_depth >= 2:
            # For 2 or fewer items, or max recursion depth, return as individual locations
            return locations

        # Create a unique key for this group to avoid infinite loops
        group_key = tuple(sorted(id(loc) for loc in locations))
        if group_key in self._processed_groups:
            return locations

        self._processed_groups.add(group_key)

        # Find the optimal threshold deterministically
        optimal_threshold = self._find_optimal_split_threshold(locations)

        # Temporarily set the threshold and re-run clustering
        original_threshold_config = self.config["similarity_threshold"]
        self.config["similarity_threshold"] = optimal_threshold

        # Re-run clustering on this group
        reclustered_groups = self._find_duplicate_groups(locations)

        # Restore original threshold
        self.config["similarity_threshold"] = original_threshold_config

        # If we got multiple clusters, process each one
        if len(reclustered_groups) > 1:
            result_locations = []

            for group_idx, group in enumerate(reclustered_groups):
                if len(group) == 1:
                    # Single location, add as-is
                    result_locations.append(locations[group[0]])
                else:
                    # Multiple locations, try to merge this subgroup
                    subgroup_locations = [locations[i] for i in group]

                    # Check if this subgroup can be merged
                    subgroup_avg_sim = self._calculate_merge_confidence(
                        subgroup_locations
                    )

                    if subgroup_avg_sim >= optimal_threshold:
                        # Merge the subgroup
                        merged_location = self._merge_location_group(subgroup_locations)
                        result_locations.append(merged_location)
                    else:
                        # Add as individual locations
                        result_locations.extend(subgroup_locations)

            return result_locations
        else:
            # Could not split the group with optimal threshold, return as individuals
            return locations

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

    def _address_similarity(self, addr1: str, addr2: str) -> float:
        """
        Calculate similarity between two addresses.

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not addr1 or not addr2:
            return 0.0

        # Normalize addresses
        norm1 = self._normalize_address(addr1)
        norm2 = self._normalize_address(addr2)

        # Exact match after normalization
        if norm1 == norm2:
            return 1.0

        # Fuzzy matching
        fuzzy_score = SequenceMatcher(None, norm1, norm2).ratio()

        # Check for street name matches
        street1 = self._extract_street_name(norm1)
        street2 = self._extract_street_name(norm2)

        if street1 and street2 and street1 == street2:
            fuzzy_score = max(fuzzy_score, 0.8)

        # Check for neighborhood/district matches
        neighborhood1 = self._extract_neighborhood(norm1)
        neighborhood2 = self._extract_neighborhood(norm2)

        if neighborhood1 and neighborhood2 and neighborhood1 == neighborhood2:
            fuzzy_score = max(fuzzy_score, 0.6)

        return fuzzy_score

    def _normalize_address(self, address: str) -> str:
        """
        Normalize address for comparison.
        """
        if not address:
            return ""

        # Convert to lowercase
        normalized = address.lower()

        # Remove common prefixes/suffixes
        prefixes = ["the ", "le ", "la ", "les ", "du ", "de ", "des "]
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :]
                break

        # Standardize common words
        replacements = {
            "street": "st",
            "avenue": "ave",
            "road": "rd",
            "boulevard": "blvd",
            "drive": "dr",
            "lane": "ln",
            "place": "pl",
            "court": "ct",
            "square": "sq",
            "circle": "cir",
            "terrace": "ter",
            "heights": "hts",
            "parkway": "pkwy",
        }

        for old, new in replacements.items():
            normalized = re.sub(r"\b" + old + r"\b", new, normalized)

        # Remove extra whitespace and punctuation
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def _extract_street_name(self, address: str) -> str:
        """
        Extract street name from address.
        """
        # Simple extraction - look for common street indicators
        words = address.split()
        for i, word in enumerate(words):
            if word in [
                "st",
                "ave",
                "rd",
                "blvd",
                "dr",
                "ln",
                "pl",
                "ct",
                "sq",
                "cir",
                "ter",
                "hts",
                "pkwy",
            ]:
                if i > 0:
                    return " ".join(words[:i])
        return ""

    def _extract_neighborhood(self, address: str) -> str:
        """
        Extract neighborhood/district from address.
        """
        # Look for common neighborhood indicators
        words = address.split()
        for i, word in enumerate(words):
            if word in ["district", "neighborhood", "area", "quarter", "borough"]:
                if i > 0:
                    return " ".join(words[:i])
        return ""

    def _geographic_distance_penalty(
        self, loc1: Dict[str, Any], loc2: Dict[str, Any]
    ) -> float:
        """
        Calculate geographic distance penalty for locations.

        Returns:
            Penalty score between 0.0 and 0.3
        """
        lat1 = loc1.get("latitude", 0)
        lon1 = loc1.get("longitude", 0)
        lat2 = loc2.get("latitude", 0)
        lon2 = loc2.get("longitude", 0)

        # If either location has no coordinates, no penalty
        if lat1 == 0 and lon1 == 0 or lat2 == 0 and lon2 == 0:
            return 0.0

        # Calculate distance in kilometers
        try:
            import math

            R = 6371  # Earth's radius in kilometers

            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)

            a = (
                math.sin(delta_lat / 2) ** 2
                + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c

            # Apply penalty based on distance
            if distance < 0.1:  # Less than 100 meters
                return 0.0
            elif distance < 1.0:  # Less than 1 km
                return 0.05
            elif distance < 5.0:  # Less than 5 km
                return 0.15
            elif distance < 10.0:  # Less than 10 km
                return 0.25
            else:  # More than 10 km
                return 0.3

        except Exception:
            return 0.0  # No penalty if calculation fails

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

Are these the same location? Consider CRITICALLY:
1. **Geographic distinctness**: Different addresses, neighborhoods, or districts indicate DIFFERENT locations
2. **Name variations**: Only merge if names are clearly variations of the same place (e.g., "Louvre Museum" vs "Musée du Louvre")
3. **Address differences**: Different street addresses almost always indicate different locations
4. **Type variations**: Same place with different type descriptions (e.g., "museum" vs "gallery" for same institution)
5. **Description differences**: Same place, different descriptions
6. **Brand name variations**: Common naming patterns and abbreviations
7. **Geographic proximity**: Locations far apart are likely different

IMPORTANT: When in doubt, prefer NOT merging. It's better to have separate entries than to incorrectly merge different locations.

CRITICAL: Respond with ONLY a valid JSON object. Do not include any explanatory text, markdown formatting, or additional content outside the JSON.

{{
    "are_same_location": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation focusing on geographic and address differences"
}}"""

            # Use max_completion_tokens for o4 models, max_tokens for others
            if self.llm_model.startswith("o4"):
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a location deduplication expert. Respond only with valid JSON. Do not include any explanatory text, markdown formatting, or additional content outside the JSON object.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=200,
                    calling_module="LocationDeduplicator",
                    operation_type="similarity_check",
                )
            else:
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a location deduplication expert. Respond only with valid JSON. Do not include any explanatory text, markdown formatting, or additional content outside the JSON object.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=200,
                    temperature=0.1,
                    calling_module="LocationDeduplicator",
                    operation_type="similarity_check",
                )

            response_text = response.choices[0].message.content.strip()

            # Clean the response if it's wrapped in markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

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
            return False  # Default to NOT merge if no LLM or single location

        # Early termination for very dissimilar groups
        avg_similarity = self._calculate_merge_confidence(locations)
        if avg_similarity < 0.3:  # Very low similarity
            print(
                f"    ⚡ Early termination: group similarity {avg_similarity:.3f} < 0.3"
            )
            return False

        max_retries = 3
        retry_delay = 1.0  # seconds

        for attempt in range(max_retries):
            try:
                # Create a summary of the locations
                location_summary = []
                for i, loc in enumerate(locations, 1):
                    summary = f"{i}. {loc.get('name', 'Unknown')} ({loc.get('type', 'Unknown')})"
                    if loc.get("address"):
                        summary += f" - {loc.get('address')}"
                    location_summary.append(summary)

                prompt = f"""You are a location deduplication expert. Review this group of locations that were flagged as potential duplicates:

{chr(10).join(location_summary)}

Are these all the same location? Consider CRITICALLY:
- **Geographic distinctness**: Different addresses, neighborhoods, or districts indicate DIFFERENT locations
- **Name variations**: Only merge if names are clearly variations of the same place (e.g., "Louvre Museum" vs "Musée du Louvre")
- **Address differences**: Different street addresses almost always indicate different locations
- **Type variations**: Same place with different type descriptions (e.g., "museum" vs "gallery" for same institution)
- **Missing information**: Don't merge if one location has much more detail than another
- **Brand name variations**: Common naming patterns and abbreviations
- **Geographic context**: Regional naming conventions and local variations

IMPORTANT: When in doubt, prefer NOT merging. It's better to have separate entries than to incorrectly merge different locations.

CRITICAL: Respond with ONLY a valid JSON object. Do not include any explanatory text, markdown formatting, or additional content outside the JSON.

{{
    "should_merge": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation focusing on geographic and address differences",
    "suggested_name": "best name for merged location (if merging)"
}}"""

                # Use max_completion_tokens for o4 models, max_tokens for others
                if self.llm_model.startswith("o4"):
                    response = self.llm_client.chat.completions.create(
                        model=self.llm_model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a location deduplication expert. Respond only with valid JSON. Do not include any explanatory text, markdown formatting, or additional content outside the JSON object.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        max_completion_tokens=300,
                        calling_module="LocationDeduplicator",
                        operation_type="group_validation",
                    )
                else:
                    response = self.llm_client.chat.completions.create(
                        model=self.llm_model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a location deduplication expert. Respond only with valid JSON. Do not include any explanatory text, markdown formatting, or additional content outside the JSON object.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=300,
                        temperature=0.1,
                        calling_module="LocationDeduplicator",
                        operation_type="group_validation",
                    )

                response_text = response.choices[0].message.content.strip()

                # Clean the response if it's wrapped in markdown
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                elif response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                # Try to parse JSON response
                import json

                try:
                    result = json.loads(response_text)
                    should_merge = bool(
                        result.get("should_merge", False)
                    )  # Default to NOT merge

                    if should_merge:
                        print(
                            f"    🤖 LLM approved merge (confidence: {result.get('confidence', 0.0):.2f})"
                        )
                    else:
                        print(
                            f"    🤖 LLM rejected merge: {result.get('reasoning', 'No reason provided')}"
                        )

                    return should_merge

                except json.JSONDecodeError:
                    print(
                        f"    ⚠️  LLM response not valid JSON (attempt {attempt + 1}/{max_retries})"
                    )
                    if attempt < max_retries - 1:
                        import time

                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue

                    # Final fallback: look for keywords in response
                    response_lower = response_text.lower()
                    if "merge" in response_lower and "same" in response_lower:
                        print("    🤖 LLM fallback: keywords suggest merge")
                        return True
                    elif "different" in response_lower or "separate" in response_lower:
                        print("    🤖 LLM fallback: keywords suggest no merge")
                        return False
                    else:
                        print("    🤖 LLM fallback: defaulting to NO merge")
                        return False

            except Exception as e:
                print(
                    f"    ⚠️  LLM group validation failed (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    import time

                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    print(
                        "    🤖 LLM validation failed after all retries, defaulting to NO merge"
                    )
                    return False

        # Should never reach here, but just in case
        print("    🤖 LLM validation failed, defaulting to NO merge")
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
        """Reset all statistics and caches for a fresh run."""
        self.stats = {
            "processed": 0,
            "duplicates_found": 0,
            "groups_created": 0,
            "false_positives": 0,
        }
        self.merge_details = []
        self._similarity_cache.clear()
        self._processed_groups.clear()
