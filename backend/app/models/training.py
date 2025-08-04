from datetime import datetime
from typing import Dict, Any, Optional

class Training:
    def __init__(
        self,
        name: str,
        description: str,
        type: str,
        agent_id: str,
        status: str = 'pending',
        progress: int = 0,
        training_data: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        logs: Optional[str] = None,
        created_at: Optional[datetime] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        self.name = name
        self.description = description
        self.type = type
        self.agent_id = agent_id
        self.status = status
        self.progress = progress
        self.training_data = training_data or {}
        self.parameters = parameters or {}
        self.metrics = metrics or {}
        self.logs = logs or ''
        self.created_at = created_at or datetime.utcnow()
        self.started_at = started_at
        self.completed_at = completed_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'agent_id': self.agent_id,
            'status': self.status,
            'progress': self.progress,
            'training_data': self.training_data,
            'parameters': self.parameters,
            'metrics': self.metrics,
            'logs': self.logs,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Training':
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            type=data.get('type', ''),
            agent_id=data.get('agent_id', ''),
            status=data.get('status', 'pending'),
            progress=data.get('progress', 0),
            training_data=data.get('training_data', {}),
            parameters=data.get('parameters', {}),
            metrics=data.get('metrics', {}),
            logs=data.get('logs', ''),
            created_at=data.get('created_at'),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at')
        ) 