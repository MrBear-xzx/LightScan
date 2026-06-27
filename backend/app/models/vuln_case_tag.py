from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VulnCaseTag(Base):
    __tablename__ = 'vuln_case_tags'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, ForeignKey('vuln_cases.case_id', ondelete='CASCADE'), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('vuln_tags.tag_id', ondelete='CASCADE'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
