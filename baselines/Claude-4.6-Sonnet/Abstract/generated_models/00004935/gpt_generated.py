import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base_radius   = 40.0   # large base circle radius
        base_height   = 20.0   # base extrusion height
        top_radius    = 30.0   # slightly smaller top circle radius
        top_height    = 15.0   # top extrusion height
    
        # --- Step 1: Create the base large extruded circle (cylinder) ---
        base = (
            cq.Workplane("XY")
            .circle(base_radius)
            .extrude(base_height)
        )
    
        # --- Step 2: Create a slightly smaller extruded circle on top ---
        result = (
            base
            .faces(">Z")
            .workplane()
            .circle(top_radius)
            .extrude(top_height)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        expected_xlen = 2 * base_radius   # 80mm — base dominates X
        expected_ylen = 2 * base_radius   # 80mm — base dominates Y
        expected_zlen = base_height + top_height  # 35mm total height
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"BBox X: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"BBox Y: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"BBox Z: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmin - 0.0) < TOL, \
            f"BBox zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - expected_zlen) < TOL, \
            f"BBox zmax: expected {expected_zlen}, got {bb.zmax}"
    
        # Volume check: base cylinder + top cylinder
        base_vol = math.pi * base_radius**2 * base_height
        top_vol  = math.pi * top_radius**2  * top_height
        expected_vol = base_vol + top_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: 
        # Base cylinder: 1 bottom flat + 1 curved side + 1 annular ring top (where top sits) + 1 top flat of base (annular)
        # Actually: base has bottom circle, curved side, and the annular top face (ring around top cylinder base)
        # Top cylinder: curved side + top circle
        # Total planar faces: bottom (1) + annular ring (1) + top of top cylinder (1) = 3 planar faces
        # Total cylindrical faces: base side (1) + top side (1) = 2 cylindrical faces
        planar_faces = result.faces("%Plane").size()
        cyl_faces    = result.faces("%Cylinder").size()
    
        assert planar_faces == 3, \
            f"Planar faces: expected 3, got {planar_faces}"
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Total face count = 5
        total_faces = result.faces().size()
        assert total_faces == 5, \
            f"Total faces: expected 5, got {total_faces}"
    
        # Circular edges check: 
        # bottom circle of base, top circle of base (inner ring bottom), 
        # top circle of base (inner ring top = bottom of top cyl), top circle of top cyl
        # = 4 circular edges
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 4, \
            f"Circular edges: expected 4, got {circ_edges}"
    
        # Center of mass should be on Z axis (x=0, y=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
    
        # CoM Z should be between 0 and total height
        assert 0 < com.z < expected_zlen, \
            f"CoM Z: expected between 0 and {expected_zlen}, got {com.z}"
    
        # Verify top cylinder is smaller: top face radius check via bounding box at top
        # The top face (>Z) should have a bounding box of 2*top_radius in X and Y
        top_face_bb = result.faces(">Z").val().BoundingBox()
        assert abs(top_face_bb.xlen - 2 * top_radius) < TOL, \
            f"Top face X span: expected {2*top_radius}, got {top_face_bb.xlen}"
        assert abs(top_face_bb.ylen - 2 * top_radius) < TOL, \
            f"Top face Y span: expected {2*top_radius}, got {top_face_bb.ylen}"
    
        # Verify bottom face is the large base circle
        bot_face_bb = result.faces("<Z").val().BoundingBox()
        assert abs(bot_face_bb.xlen - 2 * base_radius) < TOL, \
            f"Bottom face X span: expected {2*base_radius}, got {bot_face_bb.xlen}"
        assert abs(bot_face_bb.ylen - 2 * base_radius) < TOL, \
            f"Bottom face Y span: expected {2*base_radius}, got {bot_face_bb.ylen}"
    
        print("All assertions passed!")
        print(f"  Base cylinder: r={base_radius}, h={base_height}")
        print(f"  Top  cylinder: r={top_radius},  h={top_height}")
        print(f"  Total height:  {expected_zlen}")
        print(f"  Total volume:  {actual_vol:.2f} mm³")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00004935/gpt_generated.stl')
