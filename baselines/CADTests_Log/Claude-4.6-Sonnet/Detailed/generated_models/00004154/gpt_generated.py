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
        length = 0.70588
        width  = 0.40809
        height = 0.22059
        fillet_r = 0.08
    
        # --- Step 1: Create the box centered at origin ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Fillet the vertical edges (parallel to Z axis) ---
        result = result.edges("|Z").fillet(fillet_r)
    
        # --- Step 3: Translate so the base is centered at the origin (base at Z=0) ---
        # Box is currently centered at Z=0, so base is at Z = -height/2
        # Translate up by height/2 to bring base to Z=0
        result = result.translate((0, 0, height / 2))
    
        # --- Final object verification ---
        TOL = 0.001
    
        shape = result.val()
        bb = shape.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # Base should be at Z=0 (centered at origin in XY)
        assert abs(bb.zmin) < TOL, f"Base Z: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"Top Z: expected {height}, got {bb.zmax}"
    
        # XY center should be at origin
        center = shape.CenterOfBoundBox()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z - height / 2) < TOL, f"Center Z: expected {height/2}, got {center.z}"
    
        # Vertical edges (|Z) should be filleted — no straight vertical edges remain
        # After filleting, the vertical edges become cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 4, f"Cylindrical faces (from vertical fillets): expected 4, got {cyl_faces}"
    
        # Volume check: box volume minus corner material removed by fillets
        # Each vertical fillet removes a quarter-cylinder of radius r and height h
        # 4 corners × (r² - π*r²/4) × h = 4 × r² × (1 - π/4) × h
        box_vol = length * width * height
        corner_removed = 4 * (fillet_r**2 - math.pi * fillet_r**2 / 4) * height
        expected_vol = box_vol - corner_removed
        actual_vol = shape.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00004154/gpt_generated.stl')
