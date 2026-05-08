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
        diameter = 1.5
        radius = diameter / 2.0       # 0.75
        height = 0.440903
    
        # --- Step 1: Create cylinder with axis along X-axis ---
        # The 'direct' parameter sets the axis direction of the cylinder.
        # By default it's (0,0,1) (Z-axis). We set it to (1,0,0) for X-axis alignment.
        result = cq.Workplane("XY").cylinder(height, radius, direct=(1, 0, 0))
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks:
        # Along X-axis (the cylinder axis): length should equal height = 0.440903
        assert abs(bb.xlen - height) < TOL, f"X length (axis): expected {height}, got {bb.xlen}"
        # Along Y and Z (the diameter): should equal 1.5
        assert abs(bb.ylen - diameter) < TOL, f"Y length (diameter): expected {diameter}, got {bb.ylen}"
        assert abs(bb.zlen - diameter) < TOL, f"Z length (diameter): expected {diameter}, got {bb.zlen}"
    
        # Volume check: V = pi * r^2 * h
        expected_vol = math.pi * radius**2 * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a cylinder has 3 faces (2 flat circular ends + 1 curved lateral face)
        face_count = result.faces().size()
        assert face_count == 3, f"Face count: expected 3, got {face_count}"
    
        # Check cylindrical face exists
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check 2 planar (circular end) faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, f"Planar faces: expected 2, got {planar_faces}"
    
        # Check circular edges (2 circles at the ends)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, f"Circular edges: expected 2, got {circ_edges}"
    
        # Center of mass should be at origin (cylinder is centered by default)
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Verify axis alignment: the two planar faces should have normals along X-axis
        # The planar faces at min and max X should have normals in ±X direction
        min_x_face = result.faces("<X").val()
        max_x_face = result.faces(">X").val()
        min_x_normal = min_x_face.normalAt()
        max_x_normal = max_x_face.normalAt()
        assert abs(abs(min_x_normal.x) - 1.0) < TOL, f"Min X face normal X component: expected ±1, got {min_x_normal.x}"
        assert abs(abs(max_x_normal.x) - 1.0) < TOL, f"Max X face normal X component: expected ±1, got {max_x_normal.x}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670106/gpt_generated.stl')
