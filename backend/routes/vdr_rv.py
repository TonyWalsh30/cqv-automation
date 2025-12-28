# VDR/RV Routes for CQV Workbench (Flask version)
# Create new file: backend/routes/vdr_rv.py
from flask import Blueprint, jsonify, request
from database import SessionLocal
from models import (
    VDRTemplate, VDRRequirement, RequirementVerification,
    Asset, Document
)
from datetime import datetime
# Create blueprints
vdr_bp = Blueprint('vdr', __name__, url_prefix='/api/vdr')
rv_bp = Blueprint('rv', __name__, url_prefix='/api/rv')
def get_session():
    """Helper to get a database session"""
    return SessionLocal()
# =============================================================================
# VDR TEMPLATE ENDPOINTS
# =============================================================================
@vdr_bp.route('/templates', methods=['GET'])
def list_vdr_templates():
    """List all VDR templates"""
    session = get_session()
    try:
        templates = session.query(VDRTemplate).filter(VDRTemplate.is_active == True).all()
        return jsonify({
            'success': True,
            'templates': [t.to_dict() for t in templates]
        })
    finally:
        session.close()
@vdr_bp.route('/templates/<template_id>', methods=['GET'])
def get_vdr_template(template_id):
    """Get a specific VDR template with its requirements"""
    session = get_session()
    try:
        template = session.query(VDRTemplate).filter(VDRTemplate.id == template_id).first()
        if not template:
            return jsonify({'success': False, 'error': 'VDR Template not found'}), 404
        return jsonify({
            'success': True,
            'template': template.to_dict()
        })
    finally:
        session.close()
@vdr_bp.route('/templates', methods=['POST'])
def create_vdr_template():
    """Create a new VDR template"""
    data = request.get_json()
    session = get_session()
    try:
        template = VDRTemplate(
            name=data.get('name'),
            asset_level=data.get('asset_level'),
            description=data.get('description')
        )
        session.add(template)
        session.commit()
        return jsonify({
            'success': True,
            'template': template.to_dict()
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        session.close()
@vdr_bp.route('/templates/<template_id>/requirements', methods=['POST'])
def add_vdr_requirement(template_id):
    """Add a requirement to a VDR template"""
    data = request.get_json()
    session = get_session()
    try:
        template = session.query(VDRTemplate).filter(VDRTemplate.id == template_id).first()
        if not template:
            return jsonify({'success': False, 'error': 'VDR Template not found'}), 404
        
        requirement = VDRRequirement(
            vdr_template_id=template_id,
            document_type=data.get('document_type'),
            document_name=data.get('document_name'),
            is_mandatory=data.get('is_mandatory', True),
            description=data.get('description'),
            sequence=data.get('sequence', 0)
        )
        session.add(requirement)
        session.commit()
        return jsonify({
            'success': True,
            'requirement': requirement.to_dict()
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        session.close()
@vdr_bp.route('/templates/level/<asset_level>', methods=['GET'])
def get_vdr_by_level(asset_level):
    """Get VDR template for a specific asset level"""
    session = get_session()
    try:
        template = session.query(VDRTemplate).filter(
            VDRTemplate.asset_level == asset_level,
            VDRTemplate.is_active == True
        ).first()
        if not template:
            return jsonify({'success': False, 'error': f'No VDR template for level: {asset_level}'}), 404
        return jsonify({
            'success': True,
            'template': template.to_dict()
        })
    finally:
        session.close()
# =============================================================================
# RV (REQUIREMENT VERIFICATION) ENDPOINTS
# =============================================================================
@rv_bp.route('/', methods=['GET'])
def list_rvs():
    """List all RV records with optional filters"""
    asset_id = request.args.get('asset_id')
    status = request.args.get('status')
    
    session = get_session()
    try:
        query = session.query(RequirementVerification)
        
        if asset_id:
            query = query.filter(RequirementVerification.asset_id == asset_id)
        if status:
            query = query.filter(RequirementVerification.status == status)
        
        rvs = query.all()
        
        # Enrich with requirement details
        result = []
        for rv in rvs:
            req = session.query(VDRRequirement).filter(VDRRequirement.id == rv.vdr_requirement_id).first()
            rv_dict = rv.to_dict()
            rv_dict["document_name"] = req.document_name if req else "Unknown"
            rv_dict["document_type"] = req.document_type if req else "Unknown"
            rv_dict["is_mandatory"] = req.is_mandatory if req else False
            result.append(rv_dict)
        
        return jsonify({
            'success': True,
            'rvs': result
        })
    finally:
        session.close()
@rv_bp.route('/asset/<asset_id>', methods=['GET'])
def get_rvs_for_asset(asset_id):
    """Get all RV records for a specific asset"""
    session = get_session()
    try:
        rvs = session.query(RequirementVerification).filter(
            RequirementVerification.asset_id == asset_id
        ).all()
        
        result = []
        for rv in rvs:
            req = session.query(VDRRequirement).filter(VDRRequirement.id == rv.vdr_requirement_id).first()
            rv_dict = rv.to_dict()
            rv_dict["document_name"] = req.document_name if req else "Unknown"
            rv_dict["document_type"] = req.document_type if req else "Unknown"
            rv_dict["is_mandatory"] = req.is_mandatory if req else False
            result.append(rv_dict)
        
        return jsonify({
            'success': True,
            'rvs': result
        })
    finally:
        session.close()
@rv_bp.route('/generate/<asset_id>', methods=['POST'])
def generate_rvs(asset_id):
    """
    Generate RV records for an asset by comparing VDR requirements to actual documents
    
    This is the main function that:
    1. Gets the asset and its level
    2. Finds the VDR template for that level
    3. Gets all documents for this asset
    4. Compares requirements to documents
    5. Creates RV records with status (Verified/Missing)
    """
    session = get_session()
    try:
        # 1. Get asset
        asset = session.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return jsonify({'success': False, 'error': 'Asset not found'}), 404
        
        # 2. Find VDR template for asset level
        template = session.query(VDRTemplate).filter(
            VDRTemplate.asset_level == asset.asset_level.value,
            VDRTemplate.is_active == True
        ).first()
        
        if not template:
            return jsonify({
                'success': False, 
                'error': f'No VDR template found for level: {asset.asset_level.value}'
            }), 404
        
        # 3. Get all documents for this asset
        documents = session.query(Document).filter(Document.asset_id == asset_id).all()
        doc_lookup = {doc.document_type.lower(): doc for doc in documents}
        
        # 4. Delete existing RVs for this asset (regenerate fresh)
        session.query(RequirementVerification).filter(
            RequirementVerification.asset_id == asset_id
        ).delete()
        
        # 5. Generate RVs for each requirement
        rvs = []
        rv_counter = 1
        
        for req in template.requirements:
            # Check if matching document exists
            doc_type_lower = req.document_type.lower()
            matching_doc = doc_lookup.get(doc_type_lower)
            
            if matching_doc:
                status = "Verified"
                doc_id = matching_doc.id
            else:
                status = "Missing"
                doc_id = None
            
            # Generate RV number using asset tag
            rv_number = f"RV-{asset.tag_id}-{rv_counter:03d}"
            rv_counter += 1
            
            # Create RV record
            rv = RequirementVerification(
                rv_number=rv_number,
                asset_id=asset_id,
                vdr_requirement_id=req.id,
                document_id=doc_id,
                status=status,
                notes=f"Auto-generated. Document {'found' if matching_doc else 'not found'}."
            )
            session.add(rv)
            
            rvs.append({
                "rv_number": rv_number,
                "asset_id": asset_id,
                "vdr_requirement_id": req.id,
                "document_id": doc_id,
                "status": status,
                "document_name": req.document_name,
                "document_type": req.document_type,
                "is_mandatory": req.is_mandatory,
                "notes": rv.notes
            })
        
        session.commit()
        
        # Calculate summary
        verified_count = sum(1 for rv in rvs if rv["status"] == "Verified")
        missing_count = sum(1 for rv in rvs if rv["status"] == "Missing")
        
        return jsonify({
            'success': True,
            'asset_tag': asset.tag_id,
            'asset_description': asset.description,
            'total_requirements': len(rvs),
            'verified_count': verified_count,
            'missing_count': missing_count,
            'pending_count': 0,
            'rvs': rvs
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()
@rv_bp.route('/<rv_id>', methods=['PUT'])
def update_rv(rv_id):
    """Update an RV record status"""
    data = request.get_json()
    session = get_session()
    try:
        rv = session.query(RequirementVerification).filter(RequirementVerification.id == rv_id).first()
        if not rv:
            return jsonify({'success': False, 'error': 'RV not found'}), 404
        
        if 'status' in data:
            rv.status = data['status']
        if 'notes' in data:
            rv.notes = data['notes']
        if 'verified_by' in data:
            rv.verified_by = data['verified_by']
            rv.verified_at = datetime.utcnow()
        
        rv.updated_at = datetime.utcnow()
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'RV updated successfully',
            'rv': rv.to_dict()
        })
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        session.close()