# @swipelearn/services

Business logic components for the SwipeLearn platform.

## Components

| Component | Pattern | Responsibility |
|-----------|---------|----------------|
| `ContentScraper` | Adapter | Fetch & extract blog content |
| `SummarizerAI` | Strategy | AI-powered summarization |
| `TeacherTracker` | Observer | Monitor blogs for new posts |
| `FeedService` | Service | Feed generation & card management |
| `ContentPipeline` | Orchestrator | End-to-end URL → Knowledge Card |
| `URLValidator` | Utility | URL validation and normalization |

## Install

```bash
pip install -e packages/core
pip install -e packages/services
```

## Usage

```python
from swipelearn_services import ContentPipeline, ContentScraper

async with ContentPipeline() as pipeline:
    result = await pipeline.process_url("https://blog.example.com/post")
```
