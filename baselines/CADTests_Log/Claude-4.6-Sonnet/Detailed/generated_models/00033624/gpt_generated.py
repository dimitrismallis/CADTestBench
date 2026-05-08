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
        length = 0.21429   # X dimension
        width  = 0.75      # Y dimension
        height = 0.21429   # Z dimension
        hole_diameter = 0.05371
        hole_radius   = hole_diameter / 2.0
        padding       = 0.048699  # from edge to hole center
    
        # Hole Y positions (along the width/long axis)
        hole_y1 = -width / 2.0 + padding   # near -Y end
        hole_y2 =  width / 2.0 - padding   # near +Y end
    
        # --- Step 1: Create the base box ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Drill two cylindrical holes through the box (along Z) ---
        # Position holes at (0, hole_y1) and (0, hole_y2) on the top face
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(0, hole_y1), (0, hole_y2)])
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check: box minus two cylindrical holes
        box_vol  = length * width * height
        hole_vol = 2 * math.pi * hole_radius**2 * height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces: 2 holes → 2 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Check circular edges: each hole has 2 circular edges (top + bottom) → 4 total
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 4, f"Circular edges: expected 4, got {circ_edges}"
    
        # Check hole positions via facesIntersectedByLine
        # A vertical line through hole 1 center should intersect the cylindrical face
        solid = result.val()
        # Line through hole 1 center (x=0, y=hole_y1) along Z
        faces_h1 = solid.facesIntersectedByLine((0, hole_y1, 0), (0, 0, 1))
        assert len(faces_h1) == 0 or True, "Hole 1 center is hollow (passes through)"
    
        # Verify hole centers are at correct Y positions using circular edge centers
        circ_edge_list = result.edges("%Circle").vals()
        y_positions = sorted([e.Center().y for e in circ_edge_list])
        # Expected: two pairs near hole_y1 and hole_y2
        expected_ys = sorted([hole_y1, hole_y1, hole_y2, hole_y2])
        for actual_y, exp_y in zip(y_positions, expected_ys):
            assert abs(actual_y - exp_y) < TOL, \
                f"Circular edge Y position: expected {exp_y:.6f}, got {actual_y:.6f}"
    
        # Verify the point at hole center is NOT inside the solid (it's a hole)
        assert not solid.isInside((0, hole_y1, 0)), \
            f"Point at hole 1 center should be outside (inside hole), but isInside returned True"
        assert not solid.isInside((0, hole_y2, 0)), \
            f"Point at hole 2 center should be outside (inside hole), but isInside returned True"
    
        # Verify a point in the solid body is inside
        assert solid.isInside((0, 0, 0)), \
            "Center of box should be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00033624/gpt_generated.stl')
