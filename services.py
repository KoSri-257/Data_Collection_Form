import logging
from typing import Dict, List
from config import LOG_LEVEL
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, InvalidRequestError, OperationalError, DatabaseError, ProgrammingError
from sqlalchemy.orm import Session
from schema import Create, Response, SocialMediaModel
from AES import encryption, decryption
from models import PersonalInfo, HotelInfo, AgencyInfo, PlatformInfo, SocialMediaInfo

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def create_personalinfo(input: Create, db: Session) -> PersonalInfo:
    try:
        personal_info = PersonalInfo(
            first_name=input.first_name,
            last_name=input.last_name,
            title=input.title,
            email=input.personal_email,
            eid=input.eid,
            country_code=input.country_code,
            ph_no=input.ph_no
        )
        db.add(personal_info)
        db.flush()
        logger.info(f"Created PersonalInfo with pid: {personal_info.pid}")
        return personal_info
    except IntegrityError as e:
        logger.exception("Violated Key constraint")
        raise HTTPException(status_code=409, detail=f"Integrity error: {str(e)}")
    except TypeError as e:
        logger.exception("Inappropriate type operation")
        raise HTTPException(status_code=400, detail=f"Data error: {str(e)}")
    except AttributeError as e:
        logger.exception("Accessing non-existent attribute.")
        raise HTTPException(status_code=400, detail=f"Attribute error: {str(e)}")
    except InvalidRequestError as e:
        logger.exception("Invalid queries!")
        raise HTTPException(status_code=400, detail=f"Invalid request error: {str(e)}")
    except OperationalError as e:
        logger.exception("Connection failure!")
        raise HTTPException(status_code=500, detail=f"Operational error: {str(e)}")
    except ValidationError as e:
        logger.exception("Data is not meeting validation rules.")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.exception("Error while creating PersonalInfo")
        raise HTTPException(status_code=500, detail=f"An error occurred while creating personal info: {str(e)}")
    
def create_hotelinfo(input: Create, db: Session, personal_info: PersonalInfo) -> HotelInfo:
    try:
        hotel_info = HotelInfo(
            hotel_name=input.hotel_name,
            marsha_code=input.marsha_code,
            managed_franchise=input.managed_franchise,
            country=input.country,
            state=input.state,
            city=input.city,
            zip_code=input.zip_code,
            pid=personal_info.pid,
        )
        db.add(hotel_info)
        db.flush()  # To get the hid
        logger.info(f"Created HotelInfo with hid: {hotel_info.hid}")
        return hotel_info
    except IntegrityError as e:
        logger.exception("Violated Key constraint")
        raise HTTPException(status_code=409, detail=f"Integrity error: {str(e)}")
    except TypeError as e:
        logger.exception("Inappropriate type operation")
        raise HTTPException(status_code=400, detail=f"Data error: {str(e)}")
    except AttributeError as e:
        logger.exception("Accessing non-existent attribute.")
        raise HTTPException(status_code=400, detail=f"Attribute error: {str(e)}")
    except InvalidRequestError as e:
        logger.exception("Invalid queries!")
        raise HTTPException(status_code=400, detail=f"Invalid request error: {str(e)}")
    except OperationalError as e:
        logger.exception("Connection failure!")
        raise HTTPException(status_code=500, detail=f"Operational error: {str(e)}")
    except ValidationError as e:
        logger.exception("Data is not meeting validation rules.")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.exception("Error while creating HotelInfo")
        raise HTTPException(status_code=500, detail=f"An error occurred while creating hotel info: {str(e)}")

def create_agencyinfo(input: Create, db: Session, hotel_info: HotelInfo) -> AgencyInfo:
    try:
        if not input.not_applicable:
            agency_info = AgencyInfo(
                agency_name=input.agency_name,
                primary_contact=input.primary_contact,
                primary_email=input.primary_email,
                primary_phone=input.primary_phone,
                not_applicable=input.not_applicable,
                hid=hotel_info.hid
            )
            db.add(agency_info)
            db.flush() 
            logger.info(f"Created AgencyInfo with aid: {agency_info.aid}")
            return agency_info
        return None
    except IntegrityError as e:
        logger.exception("Violated Key constraint")
        raise HTTPException(status_code=409, detail=f"Integrity error: {str(e)}")
    except TypeError as e:
        logger.exception("Inappropriate type operation")
        raise HTTPException(status_code=400, detail=f"Data error: {str(e)}")
    except AttributeError as e:
        logger.exception("Accessing non-existent attribute.")
        raise HTTPException(status_code=400, detail=f"Attribute error: {str(e)}")
    except InvalidRequestError as e:
        logger.exception("Invalid queries!")
        raise HTTPException(status_code=400, detail=f"Invalid request error: {str(e)}")
    except OperationalError as e:
        logger.exception("Connection failure!")
        raise HTTPException(status_code=500, detail=f"Operational error: {str(e)}")
    except ValidationError as e:
        logger.exception("Data is not meeting validation rules.")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.exception("Error while creating AgencyInfo")
        raise HTTPException(status_code=500, detail=f"An error occurred while creating agency info: {str(e)}")

def create_socialmediainfo(input: Create, db: Session, hotel_info: HotelInfo) -> dict: 
    try:
        platform_ids = find_platform(input.platform_inputs, db) 
        social_media_objects = [] 

        # Maintain a mapping of platform_name to SocialMediaInfo
        platform_to_info_map = {}

        for platform_name, social_media_model in input.platform_inputs.items():
            if platform_name not in platform_ids:
                raise HTTPException(status_code=400, detail=f"Platform {platform_name} not found in PlatformInfo.")
            
            social_media_info = SocialMediaInfo(
                sma_name=social_media_model.sma_name,
                sma_person=social_media_model.sma_person,
                sma_email=social_media_model.sma_email,
                sma_phone=social_media_model.sma_phone,
                pageURL=encryption(social_media_model.pageURL),
                pageID=encryption(social_media_model.pageID),
                mi_fbm=social_media_model.mi_fbm,
                added_dcube=social_media_model.added_dcube,
                hid=hotel_info.hid,
                plid=platform_ids[platform_name]
            )
            social_media_objects.append(social_media_info)
            platform_to_info_map[platform_name] = social_media_info

        db.add_all(social_media_objects)
        db.flush()
        logger.info(f"Created SocialMediaInfo with sid: {social_media_info.sid}")
        
        # Return a mapping of platform_name to social_media_info
        return platform_to_info_map
    except IntegrityError as e:
        logger.exception("Violated Key constraint")
        raise HTTPException(status_code=409, detail=f"Integrity error: {str(e)}")
    except TypeError as e:
        logger.exception("Inappropriate type operation")
        raise HTTPException(status_code=400, detail=f"Data error: {str(e)}")
    except AttributeError as e:
        logger.exception("Accessing non-existent attribute.")
        raise HTTPException(status_code=400, detail=f"Attribute error: {str(e)}")
    except InvalidRequestError as e:
        logger.exception("Invalid queries!")
        raise HTTPException(status_code=400, detail=f"Invalid request error: {str(e)}")
    except OperationalError as e:
        logger.exception("Connection failure!")
        raise HTTPException(status_code=500, detail=f"Operational error: {str(e)}")
    except ValidationError as e:
        logger.exception("Data is not meeting validation rules.")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.exception("Error while creating SocialMediaInfo")
        raise HTTPException(status_code=500, detail=f"An error occurred while creating social media info: {str(e)}")

def find_platform(platform_inputs: Dict[str, SocialMediaModel], db: Session) -> Dict[str, int]:
    try:
        platform_names = list(platform_inputs.keys())
        platform_info_list = db.query(PlatformInfo).filter(PlatformInfo.platform_name.in_(platform_names)).all()

        if len(platform_info_list) != len(platform_names):
            missing_platforms = set(platform_names) - {platform_info.platform_name for platform_info in platform_info_list}
            logger.error(f"Missing platforms: {', '.join(missing_platforms)}")
            raise HTTPException(status_code=400, detail=f"None of the platforms {', '.join(missing_platforms)} were found in PlatformInfo.")
        
        platforms_obj = {plat_info.platform_name: plat_info.plid for plat_info in platform_info_list}
        logger.info(f"Found platform IDs: {platforms_obj}")
        return platforms_obj

    except DatabaseError as e:
        logger.exception("An error occurred while accessing the database.")
        raise HTTPException(status_code=400, detail="An error occurred while fetching platform information.")
    except OperationalError as e:
        logger.exception("Operational error occurred while processing data.")
        raise HTTPException(status_code=503, detail=f"Validation error: {str(e)}")
    except ProgrammingError as e:
        logger.exception("Data is not meeting validation rules.")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        raise HTTPException(status_code=500, detail="An error occurred while fetching platform information.")

def build_personal_info(personal_info: PersonalInfo) -> dict:
    try:
        if not personal_info:
            raise ValueError("PersonalInfo object is None.")
        return {
            "first_name": personal_info.first_name,
            "last_name": personal_info.last_name,
            "title": personal_info.title,
            "personal_email": personal_info.email,
            "eid": personal_info.eid,
            "country_code": personal_info.country_code,
            "ph_no": personal_info.ph_no
        }
    except Exception as e:
        logger.exception("Error while retrieving PersonalInfo")
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving personal info: {str(e)}")

def build_hotel_info(hotel_info: HotelInfo) -> dict:
    try:
        return {
            "hotel_name": hotel_info.hotel_name,
            "marsha_code": hotel_info.marsha_code,
            "managed_franchise": hotel_info.managed_franchise,
            "country": hotel_info.country,
            "state": hotel_info.state,
            "city": hotel_info.city,
            "zip_code": hotel_info.zip_code
        }
    except Exception as e:
        logger.exception("Error while retrieving HotelInfo")
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving hotel info: {str(e)}")

def build_agency_info(agency_info: AgencyInfo) -> dict:
    try:
        return {
            "agency_name": agency_info.agency_name if agency_info else None,
            "primary_contact": agency_info.primary_contact if agency_info else None,
            "primary_email": agency_info.primary_email if agency_info else None,
            "primary_phone": agency_info.primary_phone if agency_info else None,
            "not_applicable": agency_info.not_applicable if agency_info else None
        }
    except Exception as e:
        logger.exception("Error while retrieving AgencyInfo")
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving agency info: {str(e)}")

def build_social_media_info_list(social_media_info_list: List[SocialMediaInfo], decrypted_info: Dict[int, dict], db: Session) -> dict:
    try:
        result = {}
        for sm_info in social_media_info_list:
            # Query the PlatformInfo table to get the platform_name based on plid
            platform_info = db.query(PlatformInfo).filter(PlatformInfo.plid == sm_info.plid).first() 
            if not platform_info:
                raise ValueError(f"No PlatformInfo found for plid: {sm_info.plid}")
            logger.info(f"Platfrom ID: {platform_info.platform_name} and Decrypted data: {decrypted_info.get(sm_info.plid)}")
            # Build the dictionary for this platform
            result[platform_info.platform_name] = {
                "sma_name": sm_info.sma_name,
                "sma_person": sm_info.sma_person,
                "sma_email": sm_info.sma_email,
                "sma_phone": sm_info.sma_phone,
                "pageURL": decrypted_info.get('pageURL'),
                "pageID": decrypted_info.get('pageID'),
                "mi_fbm": sm_info.mi_fbm,
                "added_dcube": sm_info.added_dcube
            }
            
        return result
    except Exception as e:
        logger.exception("Error while retrieving SocialMediaInfo")
        raise HTTPException(status_code=500, detail=f"Error while retrieving social media info: {str(e)}")

def post_info(input: Response, db: Session) -> dict:
    personal_info = create_personalinfo(input, db)
    hotel_info = create_hotelinfo(input, db, personal_info)
    agency_info = create_agencyinfo(input, db, hotel_info)
    social_media_info = create_socialmediainfo(input, db, hotel_info)
    
    response_data =  {
        "pid": personal_info.pid,
        "hid": hotel_info.hid,
        "aid": agency_info.aid if agency_info else None,
        "sid": [info.sid for info in social_media_info.values()]
    }
    logger.info(f"Successfully posted info: {response_data}")
    return response_data

def get_info(eid: str, db: Session) -> dict:
    personal_info = db.query(PersonalInfo).filter(PersonalInfo.eid == eid).first()
    if not personal_info:
        logger.error(f"PersonalInfo not found for eid {eid}")
        raise HTTPException(status_code=404, detail="PersonalInfo not found.")

    hotel_info = db.query(HotelInfo).filter(HotelInfo.pid == personal_info.pid).first()
    if not hotel_info:
        logger.error(f"HotelInfo not found for hid {personal_info.pid}")
        raise HTTPException(status_code=404, detail="HotelInfo not found.")

    agency_info = db.query(AgencyInfo).filter(AgencyInfo.hid == hotel_info.hid).first()

    social_media_info = db.query(SocialMediaInfo).filter(SocialMediaInfo.hid == hotel_info.hid).all()
    print(type(social_media_info))
    if not social_media_info:
        logger.error(f"SocialMediaInfo not found for hid {hotel_info.hid}")
        raise HTTPException(status_code=404, detail="SocialMediaInfo not found.")
    decrypted_info = {
        smi.plid: {
            'pageURL': decryption(smi.pageURL),
            'pageID': decryption(smi.pageID)
        }
        for smi in social_media_info
    }
    logger.info(f"Decrypted Info Map: {decrypted_info}")

    response_data = {
        "Personal Info": build_personal_info(personal_info),
        "Hotel Info": build_hotel_info(hotel_info),
        "Agency Info": build_agency_info(agency_info) if agency_info else None,
        "Social Media Info": build_social_media_info_list(social_media_info, decrypted_info, db),
    }   
    logger.info(f"Info retrieved successfully for sid {eid}")
    return response_data