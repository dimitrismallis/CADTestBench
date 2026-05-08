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
        length  = 100.0   # long axis (X)
        width   =  30.0   # short axis (Y)
        height  =   8.0   # extrusion height (Z)
        hole_d  =   8.0   # hole diameter
        hole_r  =   hole_d / 2.0
        # Holes positioned near each end: ±40 mm from centre along X
        hole_offset_x = 40.0
    
        # --- Step 1: Create the long rectangular base and extrude ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Add two through-holes near the ends of the rectangle ---
        # Select the top face, create a workplane, push two points symmetrically
        # near the ends, then drill through-holes.
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(-hole_offset_x, 0), (hole_offset_x, 0)])
            .hole(hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.05
    
        # 1. Bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # 2. Volume = box - 2 cylinders
        box_vol  = length * width * height
        hole_vol = 2 * math.pi * hole_r**2 * height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, (
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
        )
    
        # 3. Two cylindrical faces (one curved wall per hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # 4. Circular edges — each hole has 2 circles (top + bottom rim) → 4 total
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 4, f"Circular edges: expected 4, got {circ_edges}"
    
        # 5. Holes are actually through-holes: check that points inside the
        #    nominal cylinder volumes are NOT inside the solid.
        solid = result.val()
        # Centre of left hole, mid-height
        assert not solid.isInside((-hole_offset_x, 0, 0)), (
            "Left hole centre should be outside the solid (through-hole)"
        )
        # Centre of right hole, mid-height
        assert not solid.isInside((hole_offset_x, 0, 0)), (
            "Right hole centre should be outside the solid (through-hole)"
        )
    
        # 6. A point in the solid body (away from holes) should be inside
        assert solid.isInside((0, 0, 0)), (
            "Centre of plate should be inside the solid"
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00033624/gpt_generated.stl')
