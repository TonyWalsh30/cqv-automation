"""
B2MML XML Parser Service
Recursively parses B2MML equipment data and populates the database.
"""

from lxml import etree
from models import Asset, AssetProperty, AssetLevel
from database import SessionLocal
import os

# B2MML namespace
NAMESPACES = {'B2MML': 'http://www.mesa.org/B2MML-V0600'}

class B2MMLParser:
    """Parser for B2MML equipment information"""
    
    def __init__(self, xml_path):
        """
        Initialize parser with XML file path.
        
        Args:
            xml_path: Path to B2MML XML file
        """
        self.xml_path = xml_path
        self.db = SessionLocal()
        
    def parse_and_ingest(self):
        """
        Main method to parse XML and populate database.
        Returns count of assets ingested.
        """
        try:
            # Parse XML file
            tree = etree.parse(self.xml_path)
            root = tree.getroot()
            
            # Find the root equipment element
            root_equipment = root.find('.//B2MML:Equipment', NAMESPACES)
            
            if root_equipment is None:
                raise ValueError("No Equipment element found in XML")
            
            # Recursively process equipment hierarchy
            asset_count = self._process_equipment(root_equipment, parent_id=None)
            
            # Commit all changes
            self.db.commit()
            print(f"Successfully ingested {asset_count} assets from B2MML XML")
            
            return asset_count
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error parsing B2MML XML: {str(e)}")
        finally:
            self.db.close()
    
    def _process_equipment(self, equipment_element, parent_id=None):
        """
        Recursively process equipment elements and their children.
        
        Args:
            equipment_element: XML element representing equipment
            parent_id: ID of parent asset (None for root)
            
        Returns:
            Count of assets processed
        """
        count = 0
        
        # Extract equipment data
        tag_id = self._get_text(equipment_element, 'B2MML:ID')
        description = self._get_text(equipment_element, 'B2MML:Description')
        level_str = self._get_text(equipment_element, 'B2MML:EquipmentLevel')
        
        # Map B2MML level to ISA-88 AssetLevel enum
        asset_level = self._map_equipment_level(level_str)
        
        # Create Asset object
        asset = Asset(
            tag_id=tag_id,
            description=description,
            asset_level=asset_level,
            parent_id=parent_id
        )
        
        self.db.add(asset)
        self.db.flush()  # Flush to get the generated ID
        count += 1
        
        print(f"Created asset: {tag_id} ({asset_level.value})")
        
        # Process properties
        properties = equipment_element.findall('B2MML:EquipmentProperty', NAMESPACES)
        for prop_element in properties:
            prop_name = self._get_text(prop_element, 'B2MML:ID')
            prop_value = self._get_text(prop_element, 'B2MML:Value')
            
            asset_property = AssetProperty(
                asset_id=asset.id,
                property_name=prop_name,
                property_value=prop_value
            )
            self.db.add(asset_property)
            print(f"  Added property: {prop_name} = {prop_value}")
        
        # Recursively process child equipment
        child_equipment = equipment_element.findall('B2MML:Equipment', NAMESPACES)
        for child in child_equipment:
            count += self._process_equipment(child, parent_id=asset.id)
        
        return count
    
    def _get_text(self, element, xpath):
        """
        Safely extract text from XML element using XPath.
        
        Args:
            element: XML element to search within
            xpath: XPath expression
            
        Returns:
            Text content or empty string if not found
        """
        found = element.find(xpath, NAMESPACES)
        return found.text.strip() if found is not None and found.text else ""
    
    def _map_equipment_level(self, level_str):
        """
        Map B2MML equipment level string to AssetLevel enum.
        
        Args:
            level_str: String from B2MML XML (e.g., 'Unit', 'EquipmentModule')
            
        Returns:
            AssetLevel enum value
        """
        level_mapping = {
            'Unit': AssetLevel.UNIT,
            'EquipmentModule': AssetLevel.EQUIPMENT_MODULE,
            'ControlModule': AssetLevel.CONTROL_MODULE
        }
        
        return level_mapping.get(level_str, AssetLevel.CONTROL_MODULE)


def ingest_b2mml_file(xml_path):
    """
    Convenience function to ingest B2MML XML file.
    
    Args:
        xml_path: Path to B2MML XML file
        
    Returns:
        Number of assets ingested
    """
    parser = B2MMLParser(xml_path)
    return parser.parse_and_ingest()


if __name__ == '__main__':
    # Test the parser directly
    xml_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'bio-01-b2mml.xml')
    
    if os.path.exists(xml_file):
        print(f"Parsing {xml_file}...")
        count = ingest_b2mml_file(xml_file)
        print(f"Ingestion complete: {count} assets created")
    else:
        print(f"XML file not found: {xml_file}")
