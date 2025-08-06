from datetime import datetime
from typing import Dict, Any, Optional

class Agent:
    def __init__(
        self,
        name: str,
        description: str,
        type: str,
        model_name: str,
        status: str = 'active',
        config: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.name = name
        self.description = description
        self.type = type
        self.model_name = model_name
        self.status = status
        self.config = config or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'model_name': self.model_name,
            'status': self.status,
            'config': self.config,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        return cls(
            name=data.get('name'),
            description=data.get('description'),
            type=data.get('type'),
            model_name=data.get('model_name', 'llama2'),
            status=data.get('status', 'active'),
            config=data.get('config', {}),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        ) 