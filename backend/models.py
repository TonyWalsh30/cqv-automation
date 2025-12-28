"""
SQLAlchemy ORM models implementing ISA-88 Physical Model.
Defines the asset hierarchy and standardized properties.
"""

from sqlalchemy import Column, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid
import enum

class AssetLevel(enum.Enum):
    """ISA-88 Physical Model Levels"""
    UNIT = "Unit"
    EQUIPMENT_MODULE = "EquipmentModule"
    CONTROL_MODULE = "ControlModule"

class Asset(Base):
    """
    Core asset table representing the ISA-88 hierarchy.
    Uses recursive structure with ParentID for tree relationships.
    """
    __tablename__ = 'assets'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tag_id = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    asset_level = Column(Enum(AssetLevel), nullable=False)
    parent_id = Column(String(36), ForeignKey('assets.id'), nullable=True)
    
    # Relationships
    parent = relationship('Asset', remote_side=[id], backref='children')
    properties = relationship('AssetProperty', back_populates='asset', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Asset(tag_id={self.tag_id}, level={self.asset_level.value})>"
    
    def to_dict(self, include_children=False, include_properties=True):
        """Convert asset to dictionary representation"""
        result = {
            'id': self.id,
            'tag_id': self.tag_id,
            'description': self.description,
            'asset_level': self.asset_level.value,
            'parent_id': self.parent_id
        }
        
        if include_properties:
            result['properties'] = [prop.to_dict() for prop in self.properties]
        
        if include_children:
            result['children'] = [child.to_dict(include_children=True, include_properties=include_properties) 
                                 for child in self.children]
        
        return result

class AssetProperty(Base):
    """
    Standardized attributes for assets (simulating B2MML properties).
    Examples: Serial Number, Manufacturer, Model, Calibration Date, etc.
    """
    __tablename__ = 'asset_properties'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey('assets.id'), nullable=False)
    property_name = Column(String(100), nullable=False)
    property_value = Column(Text, nullable=False)
    
    # Relationships
    asset = relationship('Asset', back_populates='properties')
    
    def __repr__(self):
        return f"<AssetProperty(name={self.property_name}, value={self.property_value})>"
    
    def to_dict(self):
        """Convert property to dictionary representation"""
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'property_name': self.property_name,
            'property_value': self.property_value
        }
# VDR/RV Models for CQV Workbench
# Add these classes to your existing models.py file (after the existing classes)
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
# =============================================================================
# DOCUMENT MODEL (if you don't have one already)
# =============================================================================
class Document(Base):
    """
    Vendor Turnover Pack documents linked to assets.
    Tracks what documents exist for each piece of equipment.
    """
    __tablename__ = 'documents'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String(36), ForeignKey('assets.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)  # "calibration_certificate", "manual", etc.
    description = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    asset = relationship('Asset', backref='documents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'filename': self.filename,
            'document_type': self.document_type,
            'description': self.description,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
# =============================================================================
# VDR TEMPLATE MODELS
# =============================================================================
class VDRTemplate(Base):
    """
    Vendor Data Requirements Template
    Defines what documents are required for each asset level/category
    """
    __tablename__ = "vdr_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)  # "Standard Process Equipment VDR"
    asset_level = Column(String(50), nullable=False)  # "Unit", "EquipmentModule", "ControlModule"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requirements = relationship("VDRRequirement", back_populates="template", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'asset_level': self.asset_level,
            'description': self.description,
            'is_active': self.is_active,
            'requirements': [req.to_dict() for req in self.requirements]
        }
class VDRRequirement(Base):
    """
    Individual document requirement within a VDR Template
    """
    __tablename__ = "vdr_requirements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vdr_template_id = Column(String(36), ForeignKey("vdr_templates.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # "calibration_certificate", "manual", etc.
    document_name = Column(String(200), nullable=False)  # Human-readable name
    is_mandatory = Column(Boolean, default=True)  # Required vs optional
    description = Column(Text, nullable=True)
    sequence = Column(Integer, default=0)  # Display order
    
    # Relationships
    template = relationship("VDRTemplate", back_populates="requirements")
    
    def to_dict(self):
        return {
            'id': self.id,
            'vdr_template_id': self.vdr_template_id,
            'document_type': self.document_type,
            'document_name': self.document_name,
            'is_mandatory': self.is_mandatory,
            'description': self.description,
            'sequence': self.sequence
        }
# =============================================================================
# REQUIREMENT VERIFICATION (RV) MODEL
# =============================================================================
class RequirementVerification(Base):
    """
    RV Record - stores verification results
    Generated by comparing VDR requirements to actual documents
    """
    __tablename__ = "requirement_verifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rv_number = Column(String(50), unique=True, nullable=False)  # "RV-BIO500-001"
    asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    vdr_requirement_id = Column(String(36), ForeignKey("vdr_requirements.id"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True)  # Link to actual doc if found
    
    status = Column(String(50), default="Pending")  # "Verified", "Missing", "Pending Review"
    verified_by = Column(String(100), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset")
    vdr_requirement = relationship("VDRRequirement")
    document = relationship("Document")
    
    def to_dict(self):
        return {
            'id': self.id,
            'rv_number': self.rv_number,
            'asset_id': self.asset_id,
            'vdr_requirement_id': self.vdr_requirement_id,
            'document_id': self.document_id,
            'status': self.status,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'notes': self.notes
        }