from pydantic import BaseModel, EmailStr, model_validator, Field
from typing import Optional, Dict, List
import re

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
    country_code: str = Field(..., pattern=r'^\+?[0-9a-zA-Z]+$')
    ph_no: str = Field(..., pattern=r'^\d{10}$')
    # HotelInfo fields
    hotel_name: str
    marsha_code: str
    managed_franchise: str
    country: str
    state: str
    city: str
    zip_code: int
    #AgencyInfo fields
    agency_name: Optional[str] = None
    primary_contact: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    not_applicable: bool = False
    
    @model_validator(mode='before')
    def validate_fields(cls, values: dict):
        if values is None:
            return values
        if not values.get('not_applicable'):
            missing_fields = [field for field in ['agency_name', 'primary_contact', 'primary_email', 'primary_phone'] 
                              if not values.get(field)]
            if missing_fields:
                raise ValueError(f"Missing required fields for 'AgencyInfo': {', '.join(missing_fields)}")
        try:
            # Validate phone number (should be exactly 10 digits)
            phone_number = values.get('primary_phone')
            if phone_number and not re.match(r'^\d{10}$', phone_number):
                raise ValueError("Invalid phone number. It must be exactly 10 digits.")
            # Validate country code (optional "+" followed by alphanumeric characters)
            country_code = values.get('country_code')
            if country_code and not re.match(r'^\+?[0-9a-zA-Z]+$', country_code):
                raise ValueError("Invalid country code. It should start with an optional '+' followed by alphanumeric characters.")
        except ValueError as e:
            raise ValueError(f"Validation error: {str(e)}")
        
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