import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        outer_radius = 20.0    # mm
        inner_radius = 12.0    # mm (medium-sized inner radius)
        length       = 200.0   # mm (very long)
    
        # --- Step 1: Create the outer solid cylinder ---
        result = cq.Workplane("XY").circle(outer_radius).extrude(length)
    
        # --- Step 2: Cut the inner hollow cylinder through the center ---
        result = result.faces(">Z").workplane().circle(inner_radius).cutThruAll()
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X extent: expected {2*outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y extent: expected {2*outer_radius}, got {bb.ylen}"
        assert abs(bb.zlen - length) < TOL, \
            f"Z extent (length): expected {length}, got {bb.zlen}"
    
        # 2. Volume check: annular cross-section * length
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * length
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count: hollow cylinder has exactly 4 faces
        #    - 2 flat annular end caps (top and bottom)
        #    - 1 outer cylindrical face
        #    - 1 inner cylindrical face
        face_count = result.faces().size()
        assert face_count == 4, \
            f"Face count: expected 4, got {face_count}"
    
        # 4. Cylindrical faces: should be exactly 2 (outer and inner)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # 5. Planar faces: should be exactly 2 (top and bottom annular caps)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, \
            f"Planar face count: expected 2, got {planar_face_count}"
    
        # 6. Center of mass should be at the geometric center (0, 0, length/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - length / 2) < TOL, \
            f"CoM Z: expected {length/2}, got {com.z}"
    
        # 7. Inner hole check: a point inside the hollow should NOT be inside the solid
        inner_point = (0, 0, length / 2)   # center of the bore
        assert not result.val().isInside(inner_point), \
            "Inner bore point should be outside the solid (hollow check failed)"
    
        # 8. Wall material check: a point in the wall should be inside the solid
        wall_point = ((outer_radius + inner_radius) / 2, 0, length / 2)
        assert result.val().isInside(wall_point), \
            "Wall midpoint should be inside the solid (wall material check failed)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00008138/gpt_generated.stl')
