from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import File, Submission
from app.storage import get_storage

logger = logging.getLogger(__name__)


def cleanup_orphaned_submissions(db: Session, older_than_hours: int = 24) -> int:
    """Cancella submission pending > N ore senza analyze + relativi file.
    
    Ritorna numero di submission cancellate.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
    
    # Trova submission pending/error vecchie senza analyze
    orphans = db.scalars(
        select(Submission)
        .where(Submission.analysis_state.in_(["pending", "error"]))
        .where(Submission.created_at < cutoff)
    ).all()
    
    deleted_count = 0
    storage = get_storage()
    
    for sub in orphans:
        try:
            # Cancella file
            files = db.scalars(
                select(File).where(File.submission_id == sub.id)
            ).all()
            for f in files:
                try:
                    # Prova a cancellare dal storage (best-effort)
                    if hasattr(storage, "delete_file"):
                        storage.delete_file(f.storage_path)
                    else:
                        # Local storage: cancella file
                        from pathlib import Path
                        from app.core.config import get_settings
                        settings = get_settings()
                        if settings.STORAGE_BACKEND == "local":
                            path = Path(settings.LOCAL_STORAGE_PATH) / f.storage_path.lstrip("/")
                            if path.exists():
                                path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete file {f.id} from storage: {e}")
            
            # Cancella record DB (cascade cancella file/extracted/findings)
            db.delete(sub)
            deleted_count += 1
        except Exception as e:
            logger.exception(f"Failed to cleanup submission {sub.id}: {e}")
    
    if deleted_count > 0:
        db.commit()
        logger.info(f"Cleaned up {deleted_count} orphaned submissions")
    
    return deleted_count
