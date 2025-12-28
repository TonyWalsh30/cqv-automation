"""
Asset API Routes
RESTful endpoints for asset management and queries
"""

from flask import Blueprint, jsonify, request
from database import SessionLocal
from services.asset_service import AssetService
from services.b2mml_parser import ingest_b2mml_file
import os

# Create blueprint
assets_bp = Blueprint('assets', __name__, url_prefix='/api/assets')

def get_asset_service():
    """Helper to create asset service with database session"""
    db = SessionLocal()
    return AssetService(db), db

@assets_bp.route('/', methods=['GET'])
def get_all_assets():
    """
    GET /api/assets
    Returns all assets in the system
    """
    service, db = get_asset_service()
    try:
        assets = service.get_all_assets()
        return jsonify({
            'success': True,
            'count': len(assets),
            'assets': [asset.to_dict(include_children=False, include_properties=False) 
                      for asset in assets]
        })
    finally:
        db.close()

@assets_bp.route('/tag/<tag_id>', methods=['GET'])
def get_asset_by_tag(tag_id):
    """
    GET /api/assets/tag/{tag_id}
    Get specific asset by tag ID with properties
    """
    service, db = get_asset_service()
    try:
        asset = service.get_asset_by_tag_id(tag_id)
        if not asset:
            return jsonify({'success': False, 'error': 'Asset not found'}), 404
        
        return jsonify({
            'success': True,
            'asset': asset.to_dict(include_children=False, include_properties=True)
        })
    finally:
        db.close()

@assets_bp.route('/tag/<tag_id>/hierarchy', methods=['GET'])
def get_asset_hierarchy(tag_id):
    """
    GET /api/assets/tag/{tag_id}/hierarchy
    Get complete asset hierarchy starting from specified asset
    """
    service, db = get_asset_service()
    try:
        hierarchy = service.get_asset_hierarchy(tag_id)
        if not hierarchy:
            return jsonify({'success': False, 'error': 'Asset not found'}), 404
        
        return jsonify({
            'success': True,
            'hierarchy': hierarchy
        })
    finally:
        db.close()

@assets_bp.route('/units', methods=['GET'])
def get_units():
    """
    GET /api/assets/units
    Get all unit-level assets
    """
    service, db = get_asset_service()
    try:
        units = service.get_units()
        return jsonify({
            'success': True,
            'count': len(units),
            'units': [unit.to_dict(include_children=False, include_properties=False) 
                     for unit in units]
        })
    finally:
        db.close()

@assets_bp.route('/tag/<tag_id>/control-modules', methods=['GET'])
def get_control_modules(tag_id):
    """
    GET /api/assets/tag/{tag_id}/control-modules
    Get all control modules under a unit (for IQ generation)
    """
    service, db = get_asset_service()
    try:
        modules = service.get_control_modules_for_unit(tag_id)
        if not modules:
            return jsonify({
                'success': False, 
                'error': 'Unit not found or no control modules'
            }), 404
        
        return jsonify({
            'success': True,
            'count': len(modules),
            'control_modules': modules
        })
    finally:
        db.close()

@assets_bp.route('/stats', methods=['GET'])
def get_asset_stats():
    """
    GET /api/assets/stats
    Get asset statistics by level
    """
    service, db = get_asset_service()
    try:
        stats = service.get_asset_count_by_level()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    finally:
        db.close()

# Ingestion endpoint
ingest_bp = Blueprint('ingest', __name__, url_prefix='/api/ingest')

@ingest_bp.route('/b2mml', methods=['POST'])
def ingest_b2mml():
    """
    POST /api/ingest/b2mml
    Trigger B2MML XML ingestion
    
    Body (optional):
        {
            "xml_file": "path/to/file.xml"  // If not provided, uses default
        }
    """
    try:
        # Get XML file path from request or use default
        data = request.get_json() if request.is_json else {}
        xml_file = data.get('xml_file')
        
        if not xml_file:
            # Use default file
            xml_file = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 'data', 'bio-01-b2mml.xml'
            )
        
        # Check if file exists
        if not os.path.exists(xml_file):
            return jsonify({
                'success': False,
                'error': f'XML file not found: {xml_file}'
            }), 400
        
        # Ingest the file
        count = ingest_b2mml_file(xml_file)
        
        return jsonify({
            'success': True,
            'message': f'Successfully ingested {count} assets from B2MML XML',
            'asset_count': count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
