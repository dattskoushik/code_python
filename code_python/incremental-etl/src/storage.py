from typing import List, Dict, Any
from sqlalchemy import create_engine, select, insert, update, bindparam
from sqlalchemy.orm import Session
from .models import Base, CustomerDB

class Storage:
    def __init__(self, db_url: str = "sqlite:///incremental.db", **engine_kwargs):
        self.engine = create_engine(db_url, **engine_kwargs)
        self.session = Session(self.engine)

    def init_db(self):
        Base.metadata.create_all(self.engine)

    def get_current_state(self) -> Dict[int, str]:
        """
        Returns a dictionary of {id: row_hash} for all records.
        Used for fast in-memory delta detection.
        """
        stmt = select(CustomerDB.id, CustomerDB.row_hash)
        results = self.session.execute(stmt).all()
        return {row.id: row.row_hash for row in results}

    def apply_batch(self, inserts: List[Dict[str, Any]], updates: List[Dict[str, Any]]):
        """
        Applies inserts and updates in a single transaction.
        """
        try:
            if inserts:
                self.session.execute(insert(CustomerDB), inserts)

            if updates:
                # Bulk update expects a list of dictionaries.
                # We need to ensure the statement binds to the primary key 'id'.
                # In SQLAlchemy 2.0, passing a list of params to execute(update(...))
                # works if the statement has bindparams or (in some cases) automatically.
                # Safest approach for generic bulk update:
                stmt = update(CustomerDB)
                self.session.execute(stmt, updates)

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def close(self):
        self.session.close()
