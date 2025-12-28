# Seed VDR Templates Script
# Run this from backend folder: python seed_vdr.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import SessionLocal
from models import VDRTemplate, VDRRequirement
def seed_vdr_templates():
    """Create default VDR templates with standard document requirements"""
    session = SessionLocal()
    
    try:
        # Check if templates already exist
        existing = session.query(VDRTemplate).first()
        if existing:
            print("VDR templates already exist. Skipping seed.")
            return
        
        # ==========================================================================
        # UNIT LEVEL VDR TEMPLATE
        # ==========================================================================
        unit_template = VDRTemplate(
            name="Standard Unit VDR",
            asset_level="Unit",
            description="Vendor data requirements for Unit-level equipment (e.g., Bioreactor, Mixer)"
        )
        session.add(unit_template)
        session.flush()  # Get the ID
        
        unit_requirements = [
            {"document_type": "manual", "document_name": "Operating Manual", "is_mandatory": True, "sequence": 1},
            {"document_type": "maintenance_manual", "document_name": "Maintenance Manual", "is_mandatory": True, "sequence": 2},
            {"document_type": "calibration_certificate", "document_name": "Calibration Certificate", "is_mandatory": True, "sequence": 3},
            {"document_type": "fat_report", "document_name": "Factory Acceptance Test Report", "is_mandatory": True, "sequence": 4},
            {"document_type": "sat_report", "document_name": "Site Acceptance Test Report", "is_mandatory": True, "sequence": 5},
            {"document_type": "drawings", "document_name": "P&ID Drawings", "is_mandatory": True, "sequence": 6},
            {"document_type": "electrical_drawings", "document_name": "Electrical Schematics", "is_mandatory": False, "sequence": 7},
            {"document_type": "spare_parts_list", "document_name": "Spare Parts List", "is_mandatory": False, "sequence": 8},
            {"document_type": "warranty", "document_name": "Warranty Documentation", "is_mandatory": False, "sequence": 9},
            {"document_type": "material_certificate", "document_name": "Material Certificates", "is_mandatory": True, "sequence": 10},
        ]
        
        for req in unit_requirements:
            session.add(VDRRequirement(vdr_template_id=unit_template.id, **req))
        
        print(f"Created Unit template with {len(unit_requirements)} requirements")
        
        # ==========================================================================
        # EQUIPMENT MODULE VDR TEMPLATE
        # ==========================================================================
        em_template = VDRTemplate(
            name="Standard Equipment Module VDR",
            asset_level="EquipmentModule",
            description="Vendor data requirements for Equipment Modules (e.g., Pump, Valve, Sensor)"
        )
        session.add(em_template)
        session.flush()
        
        em_requirements = [
            {"document_type": "manual", "document_name": "Operating Manual", "is_mandatory": True, "sequence": 1},
            {"document_type": "calibration_certificate", "document_name": "Calibration Certificate", "is_mandatory": True, "sequence": 2},
            {"document_type": "datasheet", "document_name": "Technical Datasheet", "is_mandatory": True, "sequence": 3},
            {"document_type": "drawings", "document_name": "Installation Drawings", "is_mandatory": True, "sequence": 4},
            {"document_type": "spare_parts_list", "document_name": "Spare Parts List", "is_mandatory": False, "sequence": 5},
            {"document_type": "warranty", "document_name": "Warranty Documentation", "is_mandatory": False, "sequence": 6},
        ]
        
        for req in em_requirements:
            session.add(VDRRequirement(vdr_template_id=em_template.id, **req))
        
        print(f"Created EquipmentModule template with {len(em_requirements)} requirements")
        
        # ==========================================================================
        # CONTROL MODULE VDR TEMPLATE
        # ==========================================================================
        cm_template = VDRTemplate(
            name="Standard Control Module VDR",
            asset_level="ControlModule",
            description="Vendor data requirements for Control Modules (e.g., Controllers, PLCs, HMIs)"
        )
        session.add(cm_template)
        session.flush()
        
        cm_requirements = [
            {"document_type": "manual", "document_name": "User Manual", "is_mandatory": True, "sequence": 1},
            {"document_type": "software_documentation", "document_name": "Software Documentation", "is_mandatory": True, "sequence": 2},
            {"document_type": "configuration_backup", "document_name": "Configuration Backup", "is_mandatory": True, "sequence": 3},
            {"document_type": "network_diagram", "document_name": "Network Diagram", "is_mandatory": True, "sequence": 4},
            {"document_type": "warranty", "document_name": "Warranty Documentation", "is_mandatory": False, "sequence": 5},
        ]
        
        for req in cm_requirements:
            session.add(VDRRequirement(vdr_template_id=cm_template.id, **req))
        
        print(f"Created ControlModule template with {len(cm_requirements)} requirements")
        
        # Commit all
        session.commit()
        print("\n✅ VDR templates seeded successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding templates: {e}")
        raise
    finally:
        session.close()
if __name__ == "__main__":
    print("Seeding VDR templates...")
    seed_vdr_templates()