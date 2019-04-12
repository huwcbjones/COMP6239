from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, Query

from backend.database import sql_session
from backend.models import Message


@sql_session
def get_recent_messages(from_id: UUID, to_id: UUID, session: Session, number: Optional[int] = 10) -> List[Message]:
    query = session.query(Message).options(

    ).filter_by(from_id=from_id, to_id=to_id).order(Message.created_at)  # type: Query

    if number is not None:
        query = query.limit(number)

    return query.all()
