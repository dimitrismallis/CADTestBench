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
        base_height = 0.681818
        base_diameter = 0.681818
        base_radius = base_diameter / 2.0  # 0.340909
    
        cap_height = 0.252273
        cap_diameter = 1.5
        cap_radius = cap_diameter / 2.0  # 0.75
    
        total_height = base_height + cap_height  # 0.934091
    
        # --- Step 1: Create the base cylinder ---
        # Centered in XY, extending from Z=0 to Z=base_height
        result = (
            cq.Workplane("XY")
            .circle(base_radius)
            .extrude(base_height)
        )
    
        # --- Step 2: Create the larger cap cylinder on top ---
        # Place a circle of diameter 1.5 at the top face of the base cylinder
        # and extrude it upward by cap_height
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(cap_radius)
            .extrude(cap_height)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X and Y extents should be dominated by the cap diameter (1.5)
        assert abs(bb.xlen - cap_diameter) < TOL, \
            f"X extent: expected {cap_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - cap_diameter) < TOL, \
            f"Y extent: expected {cap_diameter}, got {bb.ylen}"
    
        # Total height
        assert abs(bb.zlen - total_height) < TOL, \
            f"Total height: expected {total_height}, got {bb.zlen}"
    
        # Z extents: base at 0, top at total_height
        assert abs(bb.zmin) < TOL, \
            f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - total_height) < TOL, \
            f"Z max: expected {total_height}, got {bb.zmax}"
    
        # Volume check: base cylinder + cap cylinder
        vol_base = math.pi * base_radius**2 * base_height
        vol_cap  = math.pi * cap_radius**2 * cap_height
        expected_vol = vol_base + vol_cap
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Should have exactly 2 cylindrical faces (one for each cylinder)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Should have 3 planar faces: bottom of base, top of base (annular ring), top of cap
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 3, \
            f"Planar faces: expected 3, got {planar_faces}"
    
        # Center of mass should be on the Z axis (x=0, y=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
    
        # The cap top face should be at total_height
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - total_height) < TOL, \
            f"Top face Z: expected {total_height}, got {top_face_z}"
    
        # The bottom face should be at z=0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z) < TOL, \
            f"Bottom face Z: expected 0, got {bot_face_z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00982481/gpt_generated.stl')
