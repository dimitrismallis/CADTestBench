import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create the right triangle profile in the ZX plane ---
        # CadQuery "ZX" plane: xDir=Z, yDir=X, normal=Y
        # moveTo(a, b) -> a along world-Z, b along world-X
        # Vertices in (Z, X) space: (0,0), (0.75,0), (0,0.75)
        # This gives a right triangle with:
        #   base = 0.75 along world-Z axis
        #   height = 0.75 along world-X axis
        result = (
            cq.Workplane("ZX")
            .moveTo(0, 0)
            .lineTo(0.75, 0)
            .lineTo(0, 0.75)
            .close()
            .extrude(0.03)
        )
    
        # --- Step 2: Translate to center along Y-axis ---
        # After extrusion on ZX plane, the solid extends in Y from 0 to 0.03.
        # Translate by -0.015 in Y to center it at Y=0.
        result = result.translate((0, -0.015, 0))
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        print(f"Bounding box: xlen={bb.xlen:.4f}, ylen={bb.ylen:.4f}, zlen={bb.zlen:.4f}")
        print(f"  xmin={bb.xmin:.4f}, xmax={bb.xmax:.4f}")
        print(f"  ymin={bb.ymin:.4f}, ymax={bb.ymax:.4f}")
        print(f"  zmin={bb.zmin:.4f}, zmax={bb.zmax:.4f}")
    
        # ZX plane: horizontal=Z, vertical=X, extrusion=Y
        # World X extent = 0.75 (triangle height along X)
        assert abs(bb.xlen - 0.75) < TOL, f"Triangle height (world X extent): expected 0.75, got {bb.xlen}"
        # World Z extent = 0.75 (triangle base along Z)
        assert abs(bb.zlen - 0.75) < TOL, f"Triangle base (world Z extent): expected 0.75, got {bb.zlen}"
        # World Y extent = 0.03 (extrusion thickness)
        assert abs(bb.ylen - 0.03) < TOL, f"Thickness (world Y extent): expected 0.03, got {bb.ylen}"
    
        # Check Y centering: ymin and ymax should be symmetric about 0
        assert abs(bb.ymin - (-0.015)) < TOL, f"Y min: expected -0.015, got {bb.ymin}"
        assert abs(bb.ymax - 0.015) < TOL, f"Y max: expected 0.015, got {bb.ymax}"
    
        # Check volume: area of right triangle * thickness = 0.5 * 0.75 * 0.75 * 0.03
        expected_vol = 0.5 * 0.75 * 0.75 * 0.03
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check face count: triangular prism has 5 faces (2 triangular + 3 rectangular)
        face_count = result.faces().size()
        assert face_count == 5, f"Face count: expected 5, got {face_count}"
    
        # Check center of mass is at Y=0 (centered along Y)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
    
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00675092/gpt_generated.stl')
