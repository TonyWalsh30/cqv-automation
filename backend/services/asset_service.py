"""
Asset Service - Business logic for asset queries and operations
"""

from models import Asset, AssetLevel
from sqlalchemy.orm import Session

class AssetService:
    """Service class for asset-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_assets(self):
        """
        Get all assets in the database.
        
        Returns:
            List of all assets
        """
        return self.db.query(Asset).all()
    
    def get_asset_by_tag_id(self, tag_id: str):
        """
        Get asset by its tag ID.
        
        Args:
            tag_id: Asset tag identifier (e.g., 'BIO-01')
            
        Returns:
            Asset object or None
        """
        return self.db.query(Asset).filter(Asset.tag_id == tag_id).first()
    
    def get_asset_by_id(self, asset_id: str):
        """
        Get asset by its database ID.
        
        Args:
            asset_id: UUID of the asset
            
        Returns:
            Asset object or None
        """
        return self.db.query(Asset).filter(Asset.id == asset_id).first()
    
    def get_asset_hierarchy(self, tag_id: str):
        """
        Get complete asset hierarchy starting from specified asset.
        
        Args:
            tag_id: Root asset tag ID
            
        Returns:
            Asset dictionary with nested children and properties
        """
        asset = self.get_asset_by_tag_id(tag_id)
        if not asset:
            return None
        
        return asset.to_dict(include_children=True, include_properties=True)
    
    def get_control_modules_for_unit(self, unit_tag_id: str):
        """
        Get all control modules under a specific unit (for IQ generation).
        This recursively finds all ControlModule level assets.
        
        Args:
            unit_tag_id: Tag ID of the unit (e.g., 'BIO-01')
            
        Returns:
            List of control module assets with properties
        """
        unit = self.get_asset_by_tag_id(unit_tag_id)
        if not unit or unit.asset_level != AssetLevel.UNIT:
            return []
        
        control_modules = []
        self._collect_control_modules(unit, control_modules)
        
        return [cm.to_dict(include_children=False, include_properties=True) 
                for cm in control_modules]
    
    def _collect_control_modules(self, asset: Asset, collection: list):
        """
        Recursively collect all control modules under an asset.
        
        Args:
            asset: Asset to search under
            collection: List to append control modules to
        """
        if asset.asset_level == AssetLevel.CONTROL_MODULE:
            collection.append(asset)
        
        # Recursively search children
        for child in asset.children:
            self._collect_control_modules(child, collection)
    
    def get_units(self):
        """
        Get all Unit-level assets.
        
        Returns:
            List of unit assets
        """
        return self.db.query(Asset).filter(Asset.asset_level == AssetLevel.UNIT).all()
    
    def get_asset_count_by_level(self):
        """
        Get count of assets by level (useful for statistics).
        
        Returns:
            Dictionary with level counts
        """
        counts = {}
        for level in AssetLevel:
            count = self.db.query(Asset).filter(Asset.asset_level == level).count()
            counts[level.value] = count
        
        return counts
