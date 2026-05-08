import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base_length = 80.0
        base_width  = 60.0
        base_height = 20.0
    
        top_length  = 60.0
        top_width   = 40.0
        top_height  = 15.0
    
        # --- Step 1: Base rectangle extruded upward ---
        result = (
            cq.Workplane("XY")
            .rect(base_length, base_width)
            .extrude(base_height)
        )
    
        # --- Step 2: Smaller rectangle on top, centered, extruded upward ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(top_length, top_width)
            .extrude(top_height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Overall bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base_length) < TOL, \
            f"Overall X: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - base_width) < TOL, \
            f"Overall Y: expected {base_width}, got {bb.ylen}"
        assert abs(bb.zlen - (base_height + top_height)) < TOL, \
            f"Overall Z: expected {base_height + top_height}, got {bb.zlen}"
    
        # Bounding box Z extents
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - (base_height + top_height)) < TOL, \
            f"Z max: expected {base_height + top_height}, got {bb.zmax}"
    
        # Volume check: base box + top box
        expected_vol = (base_length * base_width * base_height) + \
                       (top_length  * top_width  * top_height)
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: the OCCT kernel produces 11 faces for this two-tier solid:
        # 1 bottom + 4 base sides + 1 ledge (top of base minus top-tier footprint,
        # represented as a single face with inner wire) + 4 top-tier sides + 1 top = 11
        face_count = result.faces().size()
        assert face_count == 11, \
            f"Face count: expected 11, got {face_count}"
    
        # All faces should be planar (no cylinders)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == face_count, \
            f"All faces should be planar: expected {face_count}, got {planar_faces}"
    
        # Check that the bottom face is at Z=0
        bottom_faces = result.faces("<Z").size()
        assert bottom_faces == 1, \
            f"Bottom face count: expected 1, got {bottom_faces}"
    
        # Check that the top face is at Z = base_height + top_height
        top_faces = result.faces(">Z").size()
        assert top_faces == 1, \
            f"Top face count: expected 1, got {top_faces}"
    
        # Check cylindrical faces = 0 (no holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, \
            f"Cylindrical faces: expected 0, got {cyl_faces}"
    
        # Center of mass should be at X=0, Y=0 (symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
    
        # The top tier should be smaller — verify a point inside top tier exists
        # Point at center of top tier (x=0, y=0, z=base_height + top_height/2)
        top_tier_center = (0, 0, base_height + top_height / 2)
        assert result.val().isInside(top_tier_center), \
            f"Point {top_tier_center} should be inside the top tier"
    
        # A point outside the top tier but inside base tier bounding box should be OUTSIDE
        # e.g., at x = base_length/2 - 1 (inside base XY, outside top tier XY), z = base_height + 1
        outside_top = (base_length / 2 - 1, 0, base_height + 1)
        assert not result.val().isInside(outside_top), \
            f"Point {outside_top} should be outside the top tier"
    
        # A point inside the base tier
        base_tier_center = (0, 0, base_height / 2)
        assert result.val().isInside(base_tier_center), \
            f"Point {base_tier_center} should be inside the base tier"
    
        # Verify the ledge exists: a point on the ledge surface (top of base, outside top tier)
        # e.g., at x = top_length/2 + 5, y = 0, z = base_height — should be on the boundary
        ledge_point_inside = (top_length / 2 + 5, 0, base_height / 2)
        assert result.val().isInside(ledge_point_inside), \
            f"Point {ledge_point_inside} should be inside the base tier (ledge region)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997852/gpt_generated.stl')
