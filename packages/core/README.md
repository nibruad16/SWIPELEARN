# @swipelearn/core

Shared Pydantic models and schemas used across all SwipeLearn backend packages.

## Models

| Model | Description |
|-------|-------------|
| `KnowledgeCard` | Full knowledge card schema with DB fields |
| `KnowledgeCardBase` | Base card schema (title, key_points, etc.) |
| `Teacher` | Teacher/Creator profile |
| `UserProfile` | User profile and auth schemas |

## Install

```bash
pip install -e packages/core
```

## Usage

```python
from swipelearn_core.models.card import KnowledgeCardBase
from swipelearn_core.models.teacher import Teacher
```
