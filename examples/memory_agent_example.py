#!/usr/bin/env python3
"""
Example demonstrating the enhanced ExtractionAgent with memory capabilities.

This script shows how the agent can:
1. Extract locations autonomously
2. Maintain memory across multiple extractions
3. Learn from previous interactions
4. Provide context-aware extractions
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from map_locations_ai.agent.extraction_agent import ExtractionAgent


def demonstrate_memory_agent():
    """Demonstrate the memory capabilities of the ExtractionAgent."""

    # Initialize the agent with memory
    agent = ExtractionAgent()

    print("🧠 Enhanced ExtractionAgent with Memory")
    print("=" * 50)

    # First extraction - Paris locations
    print("\n📍 Extraction 1: Paris locations")
    text1 = """
    I'm planning a trip to Paris. I want to visit the Eiffel Tower,
    the Louvre Museum, and have dinner at Le Comptoir du Relais.
    I'll also check out the Arc de Triomphe and walk through
    Luxembourg Gardens.
    """

    locations1 = agent.extract_locations(text1, region="Paris")
    print(f"✅ Extracted {len(locations1)} locations:")
    for loc in locations1:
        print(f"  - {loc.name} ({loc.type}) - Confidence: {loc.confidence}")

    # Show memory summary
    memory1 = agent.get_memory_summary()
    print(f"\n📊 Memory after extraction 1:")
    print(f"  - Known locations: {memory1['unique_locations_known']}")
    print(f"  - Session duration: {memory1['session_duration_seconds']:.1f}s")

    # Second extraction - referencing previous locations
    print("\n📍 Extraction 2: Referencing previous locations")
    text2 = """
    I also want to visit the Musée d'Orsay and maybe grab coffee
    at Café de Flore. I heard the Eiffel Tower is amazing at night.
    """

    locations2 = agent.extract_locations(text2, region="Paris")
    print(f"✅ Extracted {len(locations2)} locations:")
    for loc in locations2:
        print(f"  - {loc.name} ({loc.type}) - Confidence: {loc.confidence}")
        if loc.source_type == "memory":
            print(f"    (Enhanced by memory)")

    # Third extraction - new region
    print("\n📍 Extraction 3: London locations (new region)")
    text3 = """
    Now I'm planning a London trip. I want to see Big Ben,
    visit the British Museum, and check out Borough Market.
    """

    locations3 = agent.extract_locations(text3, region="London")
    print(f"✅ Extracted {len(locations3)} locations:")
    for loc in locations3:
        print(f"  - {loc.name} ({loc.type}) - Confidence: {loc.confidence}")

    # Fourth extraction - mixed regions with memory
    print("\n📍 Extraction 4: Mixed regions with memory")
    text4 = """
    I'm thinking about both cities. In Paris, I definitely want to
    see the Louvre again. In London, I'd like to visit the Tower of London.
    """

    locations4 = agent.extract_locations(text4)
    print(f"✅ Extracted {len(locations4)} locations:")
    for loc in locations4:
        print(f"  - {loc.name} ({loc.type}) - Confidence: {loc.confidence}")
        if loc.source_type == "memory":
            print(f"    (Enhanced by memory)")

    # Show final memory summary
    final_memory = agent.get_memory_summary()
    print(f"\n📊 Final Memory Summary:")
    print(f"  - Total extractions: {final_memory['conversation_count']}")
    print(f"  - Known locations: {final_memory['unique_locations_known']}")
    print(f"  - Session duration: {final_memory['session_duration_seconds']:.1f}s")
    print(f"  - Recent locations:")
    for loc in final_memory['recent_locations'][-5:]:
        print(f"    - {loc['name']} ({loc['type']})")

    # Demonstrate user feedback
    print("\n🔄 Adding user feedback...")
    agent.add_user_feedback("Eiffel Tower", {
        "type": "landmark",
        "tags": ["tourist", "must-see", "architecture", "iconic"],
        "confidence": 0.95
    })

    # Show conversation history
    print(f"\n💬 Conversation History ({len(agent.get_conversation_history())} messages):")
    for i, msg in enumerate(agent.get_conversation_history()[-3:], 1):
        print(f"  {i}. {msg['role']}: {msg['content'][:50]}...")

    # Demonstrate memory clearing
    print("\n🧹 Clearing memory...")
    agent.clear_memory()

    # Verify memory is cleared
    cleared_memory = agent.get_memory_summary()
    print(f"✅ Memory cleared - Known locations: {cleared_memory['unique_locations_known']}")

    print("\n🎉 Memory agent demonstration complete!")


def demonstrate_autonomous_extraction():
    """Demonstrate autonomous extraction with memory assistance."""

    print("\n🤖 Autonomous Extraction with Memory")
    print("=" * 50)

    agent = ExtractionAgent()

    # Simulate autonomous extraction over time
    texts = [
        "Visit the Colosseum and Vatican Museums in Rome",
        "Also check out the Trevi Fountain and Pantheon",
        "Don't forget the Roman Forum and Sistine Chapel",
        "Maybe grab pizza at Da Michele and gelato at Giolitti"
    ]

    for i, text in enumerate(texts, 1):
        print(f"\n📍 Autonomous extraction {i}:")
        print(f"Input: {text}")

        locations = agent.extract_locations(text, region="Rome")
        print(f"✅ Extracted {len(locations)} locations:")

        for loc in locations:
            confidence_boost = " (memory enhanced)" if loc.source_type == "memory" else ""
            print(f"  - {loc.name} ({loc.type}) - Confidence: {loc.confidence}{confidence_boost}")

        # Show memory growth
        memory = agent.get_memory_summary()
        print(f"📈 Memory: {memory['unique_locations_known']} known locations")


if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("LAVI_OPENAI_KEY"):
        print("❌ Error: LAVI_OPENAI_KEY environment variable is required")
        print("Please set your OpenAI API key:")
        print("export LAVI_OPENAI_KEY='your-api-key-here'")
        sys.exit(1)

    try:
        demonstrate_memory_agent()
        demonstrate_autonomous_extraction()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
