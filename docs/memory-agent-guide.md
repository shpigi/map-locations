# Memory-Enhanced Extraction Agent Guide

## Overview

The enhanced `ExtractionAgent` now includes memory capabilities that allow it to:
- **Extract autonomously** while maintaining context across multiple interactions
- **Learn from previous extractions** to improve accuracy over time
- **Maintain conversation history** for better context understanding
- **Provide memory-assisted extraction** for higher confidence results

## Key Features

### 🧠 Memory Components

1. **Conversation History**: Tracks all user inputs and agent responses
2. **Location Memory**: Stores previously extracted locations with metadata
3. **Region Context**: Maintains geographic context across extractions
4. **Session Tracking**: Monitors session duration and activity

### 🔄 Autonomous Extraction

The agent can now extract locations autonomously while using memory to:
- Boost confidence for previously seen locations
- Apply consistent classification across extractions
- Learn from user feedback and corrections
- Maintain context across different regions

## Usage Examples

### Basic Memory Agent Usage

```python
from map_locations_ai.agent.extraction_agent import ExtractionAgent

# Initialize agent with memory
agent = ExtractionAgent()

# First extraction - builds memory
text1 = "I want to visit the Eiffel Tower and Louvre Museum in Paris"
locations1 = agent.extract_locations(text1, region="Paris")

# Second extraction - uses memory for better results
text2 = "I also want to see the Arc de Triomphe and maybe visit the Eiffel Tower at night"
locations2 = agent.extract_locations(text2, region="Paris")

# Memory-enhanced locations will have higher confidence
for loc in locations2:
    if loc.source_type == "memory":
        print(f"Enhanced by memory: {loc.name} (confidence: {loc.confidence})")
```

### Memory Management

```python
# Get memory summary
summary = agent.get_memory_summary()
print(f"Known locations: {summary['unique_locations_known']}")
print(f"Session duration: {summary['session_duration_seconds']:.1f}s")

# Get conversation history
history = agent.get_conversation_history()
for msg in history:
    print(f"{msg['role']}: {msg['content'][:50]}...")

# Get all known locations
known_locations = agent.get_known_locations()
for loc in known_locations:
    print(f"- {loc.name} ({loc.type})")

# Clear memory if needed
agent.clear_memory()
```

### User Feedback Integration

```python
# Add user feedback to improve future extractions
agent.add_user_feedback("Eiffel Tower", {
    "type": "landmark",
    "tags": ["tourist", "must-see", "architecture", "iconic"],
    "confidence": 0.95
})

# Future extractions will use this improved information
locations = agent.extract_locations("I want to see the Eiffel Tower")
```

### Context-Aware Extraction

```python
# Extract with memory context (default)
locations_with_memory = agent.extract_with_context("Visit the Louvre", "Paris")

# Extract without memory context
locations_without_memory = agent.extract_with_context(
    "Visit the Louvre", "Paris", include_memory=False
)
```

## Memory Architecture

### Data Structures

```python
class ExtractionAgent:
    # Memory components
    conversation_history: List[Dict[str, Any]] = []
    extracted_locations: List[ExtractedLocation] = []
    known_locations: Dict[str, ExtractedLocation] = {}  # name -> location
    region_context: Optional[str] = None
    session_start_time = datetime.now()
```

### Memory Flow

1. **Input Processing**: User text is added to conversation history
2. **Multi-Pass Extraction**:
   - Pass 1: Direct LLM extraction
   - Pass 2: Tool-assisted extraction
   - Pass 3: Context pattern extraction
   - Pass 4: **Memory-assisted extraction** (new)
3. **Memory Update**: New locations are stored in memory
4. **Response**: Results are returned with memory context

### Memory-Assisted Extraction

The agent uses memory to:
- **Recognize previously extracted locations** in new text
- **Boost confidence scores** for known locations
- **Apply consistent classification** across extractions
- **Use region context** to improve accuracy

## Integration with Pipeline

The `LocationPipeline` has been updated to use the memory-enhanced agent:

```python
from map_locations_ai.agent.pipeline import LocationPipeline

pipeline = LocationPipeline()

# All pipeline methods now use memory-enhanced extraction
locations = pipeline.process_text("Visit the Eiffel Tower", region="Paris")

# Access memory features through the pipeline
memory_summary = pipeline.get_memory_summary()
pipeline.add_user_feedback("Eiffel Tower", {"confidence": 0.95})
pipeline.clear_memory()
```

## Performance Benefits

### Improved Accuracy
- **Higher confidence scores** for previously seen locations
- **Consistent classification** across multiple extractions
- **Better region-specific extraction** with context

### Enhanced User Experience
- **Context-aware responses** based on conversation history
- **Learning from user feedback** for continuous improvement
- **Autonomous operation** with memory assistance

### Memory Efficiency
- **Deduplication** of locations across extractions
- **Confidence-based updates** (higher confidence overwrites lower)
- **Session-based memory** that can be cleared when needed

## Best Practices

### 1. Use Region Context
```python
# Always provide region hints for better memory context
locations = agent.extract_locations(text, region="Paris")
```

### 2. Provide User Feedback
```python
# Improve future extractions with feedback
agent.add_user_feedback(location_name, {
    "type": "corrected_type",
    "tags": ["updated", "tags"],
    "confidence": 0.9
})
```

### 3. Monitor Memory Usage
```python
# Check memory summary periodically
summary = agent.get_memory_summary()
if summary['unique_locations_known'] > 1000:
    agent.clear_memory()  # Clear if memory gets too large
```

### 4. Use Context Appropriately
```python
# Use memory for related extractions
locations_with_memory = agent.extract_with_context(text, region)

# Use fresh extraction for unrelated content
locations_fresh = agent.extract_with_context(text, region, include_memory=False)
```

## Example Workflow

```python
# 1. Initialize agent
agent = ExtractionAgent()

# 2. Extract locations with memory building
text1 = "Visit the Eiffel Tower, Louvre, and Arc de Triomphe in Paris"
locations1 = agent.extract_locations(text1, region="Paris")

# 3. Extract more locations (memory-enhanced)
text2 = "Also check out the Musée d'Orsay and maybe visit the Eiffel Tower at night"
locations2 = agent.extract_locations(text2, region="Paris")

# 4. Add user feedback
agent.add_user_feedback("Eiffel Tower", {
    "tags": ["tourist", "must-see", "architecture", "iconic"]
})

# 5. Extract in new region (memory still helps)
text3 = "Now planning London trip: Big Ben, British Museum, and Tower of London"
locations3 = agent.extract_locations(text3, region="London")

# 6. Check memory status
summary = agent.get_memory_summary()
print(f"Session: {summary['session_duration_seconds']:.1f}s")
print(f"Known locations: {summary['unique_locations_known']}")
```

## Testing

Run the memory agent tests:

```bash
# Run memory agent tests
python -m pytest tests/test_memory_agent.py -v

# Run the example
python examples/memory_agent_example.py
```

## Configuration

The memory agent uses the same configuration as the basic agent:

```python
config = {
    "model_id": "gpt-4o",
    "request_timeout": 30,
    # ... other config options
}

agent = ExtractionAgent(config)
```

Memory features are enabled by default and don't require additional configuration.
