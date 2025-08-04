from datetime import datetime
from typing import Dict, Any, Optional, List

class Workflow:
    def __init__(
        self,
        name: str,
        description: str,
        type: str,
        status: bool = True,
        definition: Optional[Dict[str, Any]] = None,
        execution_count: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.name = name
        self.description = description
        self.type = type
        self.status = status
        self.definition = definition or {}
        self.execution_count = execution_count
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'definition': self.definition,
            'execution_count': self.execution_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            type=data.get('type', ''),
            status=data.get('status', True),
            definition=data.get('definition', {}),
            execution_count=data.get('execution_count', 0),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        ) 