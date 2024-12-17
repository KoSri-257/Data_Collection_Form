from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, Dict, List

class SocialMediaModel(BaseModel):
    # SocialMediaInfo fields
    sma_name: str
    sma_person: str
    sma_email: EmailStr
    sma_phone: str
    pageURL: str
    pageID: str
    mi_fbm: bool
    added_dcube: bool

    @model_validator(mode='before')
    def validate_social_media(cls, values: dict):
        mi_fbm = values.get('mi_fbm')
        added_dcube = values.get('added_dcube')
        if mi_fbm:
            values['added_dcube'] = True
        else:
            if added_dcube is None:
                raise ValueError("'added_dcube' must be specified when 'mi_fbm' is False.")
        return values

class Base(BaseModel):
    # PersonalInfo fields
    first_name: str
    last_name: str
    title: str
    personal_email: EmailStr
    eid: str
    country_code: str
    ph_no: str
    # HotelInfo fields
    hotel_name: str
    marsha_code: str
    managed_franchise: str
    country: str
    state: str
    city: str
    zip_code: str
    #AgencyInfo fields
    agency_name: Optional[str] = None
    primary_contact: Optional[str] = None
    primary_email: Optional[str] = None
    primary_phone: Optional[str] = None
    not_applicable: bool = False
    
    @model_validator(mode='before')
    def validate_fields(cls, values: dict):
        if values is None:
            return values 
        if not values.get('not_applicable'):
            missing_fields = [field for field in ['agency_name', 'primary_contact', 'primary_email', 'primary_phone'] 
                              if not values.get(field) ]
            if missing_fields:
                raise ValueError(f"Missing required fields for 'AgencyInfo': {', '.join(missing_fields)}")
        return values

class Create(Base):
    platform_inputs: Dict[str, SocialMediaModel]

    @model_validator(mode="before")
    def validate_platforms(cls, values: dict):
        platform_inputs = values.get('platform_inputs', {})
        if not platform_inputs:
            raise ValueError("At least one platform input is required.")
        return values

class Response(Base):
    pid: int  
    hid: int
    aid: Optional[int] = None
    sid: List[int]

    class Config:
        from_attributes = True