import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create cylinder with height=0.6, diameter=1.5 (radius=0.75) ---
        # CadQuery cylinder is centered at origin by default
        result = cq.Workplane("XY").cylinder(0.6, 0.75)
    
        # --- Step 2: Shell the top face inward by 0.075 units ---
        # Select the top face (>Z) and shell inward (negative thickness)
        result = result.faces(">Z").shell(-0.075)
    
        # --- Step 3: Translate so base is centered at origin ---
        # After centering, the cylinder base is at Z = -0.3, top at Z = 0.3
        # Translate up by 0.3 so base is at Z = 0
        result = result.translate((0, 0, 0.3))
    
        # --- Final object verification ---
        TOL = 0.01
    
        shape = result.val()
        bb = shape.BoundingBox()
    
        # Bounding box checks
        # After translation: base at Z=0, top at Z=0.6
        assert abs(bb.zmin) < TOL, f"Base Z expected ~0, got {bb.zmin}"
        assert abs(bb.zmax - 0.6) < TOL, f"Top Z expected ~0.6, got {bb.zmax}"
    
        # Diameter check: xlen and ylen should be ~1.5
        assert abs(bb.xlen - 1.5) < TOL, f"X diameter expected ~1.5, got {bb.xlen}"
        assert abs(bb.ylen - 1.5) < TOL, f"Y diameter expected ~1.5, got {bb.ylen}"
    
        # Height check
        assert abs(bb.zlen - 0.6) < TOL, f"Height expected ~0.6, got {bb.zlen}"
    
        # Volume check: shelled cylinder
        # Outer cylinder volume: pi * r^2 * h = pi * 0.75^2 * 0.6
        outer_vol = math.pi * (0.75 ** 2) * 0.6
        # Inner cylinder volume (hollow part): pi * (r - wall)^2 * (h - wall)
        # wall = 0.075, inner_r = 0.75 - 0.075 = 0.675, inner_h = 0.6 - 0.075 = 0.525
        inner_r = 0.75 - 0.075
        inner_h = 0.6 - 0.075
        inner_vol = math.pi * (inner_r ** 2) * inner_h
        expected_vol = outer_vol - inner_vol
        actual_vol = shape.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume expected ~{expected_vol:.4f}, got {actual_vol:.4f}"
    
        # Check that the top is open (no face at max Z that is a full disk)
        # The top face was removed by shelling, so there should be no planar face at zmax
        # Instead there should be a ring/annular face at the top
        top_faces = result.faces(">Z").vals()
        # The top should be an annular ring (one planar face at top)
        assert len(top_faces) >= 1, f"Expected at least one face at top, got {len(top_faces)}"
    
        # Check cylindrical faces exist (outer and inner walls)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, f"Expected at least 2 cylindrical faces (inner+outer), got {cyl_faces}"
    
        # Check center of base is at origin (X=0, Y=0, Z=0)
        center = shape.CenterOfBoundBox()
        assert abs(center.x) < TOL, f"Center X expected ~0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y expected ~0, got {center.y}"
        assert abs(center.z - 0.3) < TOL, f"Center Z expected ~0.3, got {center.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520675/gpt_generated.stl')
