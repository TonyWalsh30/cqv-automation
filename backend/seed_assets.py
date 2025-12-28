# Seed Test Assets Script
# Run from backend folder: python seed_assets.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import SessionLocal
from models import Asset, AssetLevel, Document
def seed_test_assets():
    """Create test assets and documents for RV testing"""
    session = SessionLocal()
    
    try:
        # Check if assets already exist
        existing = session.query(Asset).first()
        if existing:
            print("Assets already exist. Skipping seed.")
            return
        
        # ==========================================================================
        # CREATE UNIT LEVEL ASSETS
        # ==========================================================================
        bioreactor = Asset(
            tag_id="BIO-001",
            description="500L Bioreactor System",
            asset_level=AssetLevel.UNIT
        )
        session.add(bioreactor)
        session.flush()
        
        # Add some documents for the bioreactor (partial - to test missing docs)
        bioreactor_docs = [
            {"filename": "BIO-001_Operating_Manual.pdf", "document_type": "manual", "description": "Operating manual for bioreactor"},
            {"filename": "BIO-001_Calibration_Cert.pdf", "document_type": "calibration_certificate", "description": "Calibration certificate"},
            {"filename": "BIO-001_FAT_Report.pdf", "document_type": "fat_report", "description": "Factory acceptance test report"},
        ]
        for doc in bioreactor_docs:
            session.add(Document(asset_id=bioreactor.id, **doc))
        
        print(f"Created Unit: {bioreactor.tag_id} with {len(bioreactor_docs)} documents")
        
        # ==========================================================================
        # CREATE ANOTHER UNIT
        # ==========================================================================
        mixer = Asset(
            tag_id="MIX-001",
            description="High Shear Mixer",
            asset_level=AssetLevel.UNIT
        )
        session.add(mixer)
        session.flush()
        
        # Add ALL required documents (to test verified status)
        mixer_docs = [
            {"filename": "MIX-001_Manual.pdf", "document_type": "manual"},
            {"filename": "MIX-001_Maintenance.pdf", "document_type": "maintenance_manual"},
            {"filename": "MIX-001_Cal.pdf", "document_type": "calibration_certificate"},
            {"filename": "MIX-001_FAT.pdf", "document_type": "fat_report"},
            {"filename": "MIX-001_SAT.pdf", "document_type": "sat_report"},
            {"filename": "MIX-001_PID.pdf", "document_type": "drawings"},
            {"filename": "MIX-001_Materials.pdf", "document_type": "material_certificate"},
        ]
        for doc in mixer_docs:
            session.add(Document(asset_id=mixer.id, **doc))
        
        print(f"Created Unit: {mixer.tag_id} with {len(mixer_docs)} documents")
        
        # ==========================================================================
        # CREATE EQUIPMENT MODULE
        # ==========================================================================
        pump = Asset(
            tag_id="PMP-001",
            description="Feed Pump Assembly",
            asset_level=AssetLevel.EQUIPMENT_MODULE
        )
        session.add(pump)
        session.flush()
        
        pump_docs = [
            {"filename": "PMP-001_Manual.pdf", "document_type": "manual"},
            {"filename": "PMP-001_Datasheet.pdf", "document_type": "datasheet"},
        ]
        for doc in pump_docs:
            session.add(Document(asset_id=pump.id, **doc))
        
        print(f"Created EquipmentModule: {pump.tag_id} with {len(pump_docs)} documents")
        
        # ==========================================================================
        # CREATE CONTROL MODULE
        # ==========================================================================
        plc = Asset(
            tag_id="PLC-001",
            description="Main Process Controller",
            asset_level=AssetLevel.CONTROL_MODULE
        )
        session.add(plc)
        session.flush()
        
        plc_docs = [
            {"filename": "PLC-001_Manual.pdf", "document_type": "manual"},
            {"filename": "PLC-001_Software.pdf", "document_type": "software_documentation"},
        ]
        for doc in plc_docs:
            session.add(Document(asset_id=plc.id, **doc))
        
        print(f"Created ControlModule: {plc.tag_id} with {len(plc_docs)} documents")
        
        # Commit all
        session.commit()
        print("\n✅ Test assets seeded successfully!")
        print("\nAsset Summary:")
        print("  - BIO-001 (Unit): 3 docs - expect 7 missing")
        print("  - MIX-001 (Unit): 7 docs - expect 3 missing")
        print("  - PMP-001 (EquipmentModule): 2 docs - expect 4 missing")
        print("  - PLC-001 (ControlModule): 2 docs - expect 3 missing")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding assets: {e}")
        raise
    finally:
        session.close()
if __name__ == "__main__":
    print("Seeding test assets...")
    seed_test_assets()