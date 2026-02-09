from pydantic import BaseModel
from typing import Optional, List

class PropertyData(BaseModel):
    """Property data model"""
    id: str
    url: str
    type: str  # villa, condo, house, land
    price_usd: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    size_sqm: Optional[float] = None
    land_size_sqm: Optional[float] = None
    ownership_type: Optional[str] = None  # hard_title, soft_title, strata_title
    floor_level: Optional[int] = None
    location: Optional[str] = None
    
    # Computed fields
    has_land: bool = False
    is_foreign_eligible_direct: bool = False
    recommended_structures: List[str] = []
    
    def compute_eligibility(self):
        """Determine if foreigner can own directly"""
        if self.type == "condo" and self.floor_level and self.floor_level >= 2:
            self.is_foreign_eligible_direct = True
            self.recommended_structures = ["strata_title"]
        elif self.type == "villa" or (self.type == "condo" and self.floor_level == 1):
            self.is_foreign_eligible_direct = False
            self.has_land = True
            self.recommended_structures = ["leasehold", "company_structure"]
        elif self.type == "land":
            self.is_foreign_eligible_direct = False
            self.has_land = True
            self.recommended_structures = ["leasehold", "company_structure"]
        
        return self
