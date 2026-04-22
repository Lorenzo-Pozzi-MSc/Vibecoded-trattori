"""
data/models.py — Data models for tractors and machines

Provides structured, type-safe representations of tractors and implements.
These models enforce data consistency and make the codebase easier to understand.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd



@dataclass
class Tractor:
    """
    A tractor with its specifications.
    
    Represents a single tractor model with key technical information
    like power, traction type, and attachment capabilities.
    """
    name: str
    """The model name or series"""
    
    brand: str = ""
    """The manufacturer/brand name"""
    
    traction_type: list[str] = field(default_factory=list)
    """Types of traction available (e.g. ['2WD', '4WD'])"""
    
    power_min_cv: Optional[float] = None
    """Minimum power in CV (cavalli vapore / horsepower)"""
    
    power_max_cv: Optional[float] = None
    """Maximum power in CV"""
    
    turning_radius_m: Optional[float] = None
    """Minimum turning radius in meters"""
    
    attachment_categories: list[str] = field(default_factory=list)
    """Available 3-point hitch categories (e.g. ['1', '2', '3'])"""

    pto_speeds: list[str] = field(default_factory=list)
    """Available PTO speeds (e.g. ['540', '1000'])"""
    
    link: Optional[str] = None
    """URL to technical sheet or product page"""
    
    raw_data: dict = field(default_factory=dict)
    """All raw data from the Excel row (for future extensions)"""
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not self.name:
            raise ValueError("Tractor name is required")


@dataclass
class Machine:
    """
    An implement or machine with its specifications.
    
    Represents a single implement/machine that can attach to a tractor,
    with requirements and capabilities.
    """
    name: str
    """The model name"""
    
    manufacturer: str = ""
    """The manufacturer name"""
    
    operation_type: str = ""
    """Type of operation (plowing, harvesting, etc.)"""
    
    machine_type: str = ""
    """Type of machine/implement"""
    
    min_power_required_hp: Optional[float] = None
    """Minimum tractor power required in HP"""
    
    max_power_recommended_hp: Optional[float] = None
    """Maximum recommended tractor power in HP"""
    
    min_work_width_m: Optional[float] = None
    """Minimum working width in meters"""
    
    max_work_width_m: Optional[float] = None
    """Maximum working width in meters"""
    
    min_turning_radius_m: Optional[float] = None
    """Minimum turning radius required in meters"""
    
    attachment_type: str = ""
    """How it attaches to the tractor (3-point hitch category, etc.)"""
    
    is_foldable: bool = False
    """Whether the implement can be folded for transport"""
    
    technical_sheet_url: Optional[str] = None
    """URL to the manufacturer's technical sheet"""
    
    raw_data: dict = field(default_factory=dict)
    """All raw data from the Excel row (for future extensions)"""
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not self.name:
            raise ValueError("Machine name is required")


class TractorDatabase:
    """
    Container for all tractors with both model and DataFrame access.
    
    Provides type-safe access through Tractor models while maintaining
    the underlying DataFrame for efficient matching operations.
    """
    
    def __init__(self, tractors: list[Tractor], dataframe: pd.DataFrame):
        """
        Create a tractor database.
        
        Args:
            tractors: List of Tractor model instances
            dataframe: The underlying pandas DataFrame (for matching logic)
        """
        self.tractors = tractors
        """List of all tractor models"""
        
        self.dataframe = dataframe
        """The underlying DataFrame for matching/filtering operations"""
    
    def __len__(self) -> int:
        """Return the number of tractors."""
        return len(self.tractors)
    
    def __getitem__(self, index: int) -> Tractor:
        """Get a tractor by index."""
        return self.tractors[index]
    
    def get_by_brand(self, brand: str) -> list[Tractor]:
        """Get all tractors from a specific brand."""
        return [t for t in self.tractors if t.brand.lower() == brand.lower()]
    
    def get_by_traction_type(self, traction_type: str) -> list[Tractor]:
        """Get all tractors that include a specific traction type."""
        return [t for t in self.tractors if traction_type.lower() in [tt.lower() for tt in t.traction_type]]


class MachineDatabase:
    """
    Container for all machines/implements with both model and DataFrame access.
    
    Provides type-safe access through Machine models while maintaining
    the underlying DataFrame for efficient matching operations.
    """
    
    def __init__(self, machines: list[Machine], dataframe: pd.DataFrame):
        """
        Create a machine database.
        
        Args:
            machines: List of Machine model instances
            dataframe: The underlying pandas DataFrame (for matching logic)
        """
        self.machines = machines
        """List of all machine models"""
        
        self.dataframe = dataframe
        """The underlying DataFrame for matching/filtering operations"""
    
    def __len__(self) -> int:
        """Return the number of machines."""
        return len(self.machines)
    
    def __getitem__(self, index: int) -> Machine:
        """Get a machine by index."""
        return self.machines[index]
    
    def get_by_operation_type(self, op_type: str) -> list[Machine]:
        """Get all machines for a specific operation type."""
        return [m for m in self.machines if op_type.lower() in m.operation_type.lower()]
    
    def get_by_manufacturer(self, manufacturer: str) -> list[Machine]:
        """Get all machines from a specific manufacturer."""
        return [m for m in self.machines if m.manufacturer.lower() == manufacturer.lower()]
