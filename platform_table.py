import logging
from database import get_db
from config import LOG_LEVEL
from sqlalchemy.orm import Session
from models import PlatformInfo
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

platforms = ["Facebook", "Instagram", "LinkedIn", "Pinterest", "TikTok", "Twitter", "YouTube", "Other", "I don't know"]

# Populating the PlatformInfo using DB session
def populate_platform_info_session(db: Session):
        logger.info("Checking if PlatformInfo table is empty...")
        if db.query(PlatformInfo).count() > 0:
            logger.info("PlatformInfo table already populated!")
            return
        try:
            logger.info("PlatformInfo table is empty...")
            plid = 101
            for platform in platforms:
                platform_info = PlatformInfo(plid=f"{plid:04}", platform_name=platform)
                db.add(platform_info)
                plid += 1
            db.commit()
            logger.info("PlatformInfo table populated successfully!")
        except TypeError as e:
            logger.exception(f"Error with platforms data: {e}")
            raise
        except ValueError as e:
            logger.exception(f"Value error while creating platform records: {e}")
            raise
        except IntegrityError as e:
            logger.exception(f"Integrity error while adding platform record: {e}")
            raise
        except SQLAlchemyError as e:
            logger.exception(f"Error committing to the database: {e}")
            db.rollback()
            raise

# Handling DB session for populating PlatformInfo
def populate_platform_info():
    try:
        with next(get_db()) as db:
            populate_platform_info_session(db)
    except OperationalError as e:
        logger.exception(f"Database connection error: {e}")
    except SQLAlchemyError as e:
        logger.exception(f"SQLAlchemy error: {e}")
    except Exception as e:
        logger.exception(f"Error populating PlatformInfo table: {e}")
