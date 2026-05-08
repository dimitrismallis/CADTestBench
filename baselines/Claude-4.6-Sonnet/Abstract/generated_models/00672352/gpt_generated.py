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
        length   = 80.0   # X dimension
        width    = 50.0   # Y dimension
        height   = 5.0    # marginal extrusion height
        hole_d   = 6.0    # hole diameter
        margin   = 10.0   # distance from edges to hole center
    
        # --- Step 1: Draw rectangle and extrude marginally ---
        result = cq.Workplane("XY").rect(length, width).extrude(height)
    
        # --- Step 2: Create a small circular hole in the top-right corner ---
        # The rectangle is centered at origin, so:
        #   top-right corner is at (+length/2, +width/2)
        #   hole center offset inward by margin from each edge
        hole_x = length / 2 - margin   # +30
        hole_y = width  / 2 - margin   # +15
    
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(hole_x, hole_y)
            .hole(hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # 2. Volume: box minus one cylindrical hole
        box_vol  = length * width * height
        hole_vol = math.pi * (hole_d / 2) ** 2 * height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical face count: exactly 1 (the hole wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # 4. Circular edges: top and bottom circles of the hole → 2
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, f"Circular edges: expected 2, got {circ_edges}"
    
        # 5. The hole passes through: verify a point at hole center is NOT inside the solid
        hole_center_inside = result.val().isInside((hole_x, hole_y, height / 2))
        assert not hole_center_inside, \
            "Hole center should be outside (inside the hole), but isInside returned True"
    
        # 6. A point at the plate center should be inside the solid
        plate_center_inside = result.val().isInside((0.0, 0.0, height / 2))
        assert plate_center_inside, "Plate center should be inside the solid"
    
        # 7. Face count:
        #    - 6 faces for a plain box
        #    - +1 for the cylindrical hole wall
        #    - top and bottom faces remain as single faces (with inner hole wire), not split
        #    Total = 7
        total_faces = result.faces().size()
        assert total_faces == 7, f"Total faces: expected 7, got {total_faces}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00672352/gpt_generated.stl')
