import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create outer cylinder oriented horizontally (axis along X) ---
        # Use YZ plane so extrusion goes along X axis
        # Outer diameter = 0.75, radius = 0.375
        # Height (length) = 1.5
        outer_radius = 0.75 / 2       # 0.375
        inner_radius = 0.3125 / 2     # 0.15625
        length = 1.5
    
        result = (
            cq.Workplane("YZ")
            .circle(outer_radius)
            .extrude(length)
        )
    
        # --- Step 2: Cut inner hole through the full length ---
        result = (
            result
            .faces(">X")
            .workplane()
            .circle(inner_radius)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # Bounding box: X = 1.5 (length), Y = 0.75 (outer dia), Z = 0.75 (outer dia)
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - 0.75) < TOL, f"Y length (outer dia): expected 0.75, got {bb.ylen}"
        assert abs(bb.zlen - 0.75) < TOL, f"Z length (outer dia): expected 0.75, got {bb.zlen}"
    
        # Cylinder is centered at origin in Y and Z, starts at X=0
        assert abs(bb.xmin - 0.0) < TOL, f"X min: expected 0.0, got {bb.xmin}"
        assert abs(bb.xmax - length) < TOL, f"X max: expected {length}, got {bb.xmax}"
        assert abs(bb.ymin - (-outer_radius)) < TOL, f"Y min: expected {-outer_radius}, got {bb.ymin}"
        assert abs(bb.ymax - outer_radius) < TOL, f"Y max: expected {outer_radius}, got {bb.ymax}"
        assert abs(bb.zmin - (-outer_radius)) < TOL, f"Z min: expected {-outer_radius}, got {bb.zmin}"
        assert abs(bb.zmax - outer_radius) < TOL, f"Z max: expected {outer_radius}, got {bb.zmax}"
    
        # Volume check: pi * (R_outer^2 - R_inner^2) * length
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * length
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 2 flat annular end faces + 1 outer cylindrical face + 1 inner cylindrical face = 4
        face_count = result.faces().size()
        assert face_count == 4, f"Face count: expected 4, got {face_count}"
    
        # Check cylindrical faces: outer and inner cylinders
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Check planar faces: 2 annular end caps
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, f"Planar face count: expected 2, got {planar_face_count}"
    
        # Verify the hole exists: a point on the axis inside the cylinder should be OUTSIDE the solid
        # (because it's hollow). Check midpoint along X axis at center Y=0, Z=0
        mid_x = length / 2
        axis_point = (mid_x, 0.0, 0.0)
        solid_shape = result.val()
        assert not solid_shape.isInside(axis_point), \
            f"Axis point {axis_point} should be outside (inside the hole), but isInside returned True"
    
        # Verify a point in the wall IS inside the solid
        wall_point = (mid_x, (outer_radius + inner_radius) / 2, 0.0)
        assert solid_shape.isInside(wall_point), \
            f"Wall point {wall_point} should be inside the solid, but isInside returned False"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00004596/gpt_generated.stl')
