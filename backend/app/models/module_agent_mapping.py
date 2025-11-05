from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from app.db.base_class import Base

class ModuleAgentMapping(Base):
    __tablename__ = "module_agent_mapping"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, nullable=False)
    agent_id = Column(Integer, nullable=False)
    enabled = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('module_id', 'agent_id', name='_module_agent_uc'),
    )
