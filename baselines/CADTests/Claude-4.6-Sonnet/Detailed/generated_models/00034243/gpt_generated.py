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
        # --- Parameters ---
        main_diameter = 1.5
        main_radius = main_diameter / 2.0       # 0.75
        height = 0.1
        hole_diameter = 0.1124
        hole_radius = hole_diameter / 2.0       # 0.0562
        padding = 0.041187
    
        # Offset from center for each hole
        offset = main_radius / 2.0 - hole_radius - padding
        # = 0.375 - 0.0562 - 0.041187 = 0.278013
        print(f"Hole offset from center: {offset:.6f}")
    
        # --- Step 1: Create main cylinder (axis along Z, centered at origin) ---
        result = cq.Workplane("XY").cylinder(height, main_radius)
    
        # --- Step 2: Create four holes in a square layout ---
        # Holes at (±offset, ±offset) from center on the top face
        # Using pushPoints to place holes at the four corners of the square
        hole_positions = [
            (offset, offset),
            (-offset, offset),
            (-offset, -offset),
            (offset, -offset),
        ]
    
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(hole_positions)
            .hole(hole_diameter)
        )
    
        # --- Step 3: Rotate 45 degrees around Z-axis ---
        result = result.rotate((0, 0, 0), (0, 0, 1), 45)
    
        # --- Step 4: Rotate 90 degrees around Y-axis ---
        result = result.rotate((0, 0, 0), (0, 1, 0), 90)
    
        # --- Step 5: Center the part in 3D space ---
        # After rotation, check bounding box and translate to center
        bb = result.val().BoundingBox()
        cx = (bb.xmin + bb.xmax) / 2.0
        cy = (bb.ymin + bb.ymax) / 2.0
        cz = (bb.zmin + bb.zmax) / 2.0
        print(f"BBox before centering: x=[{bb.xmin:.4f},{bb.xmax:.4f}], y=[{bb.ymin:.4f},{bb.ymax:.4f}], z=[{bb.zmin:.4f},{bb.zmax:.4f}]")
        print(f"Center offset: ({cx:.4f}, {cy:.4f}, {cz:.4f})")
        result = result.translate((-cx, -cy, -cz))
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
        print(f"Final BBox: x=[{bb.xmin:.4f},{bb.xmax:.4f}], y=[{bb.ymin:.4f},{bb.ymax:.4f}], z=[{bb.zmin:.4f},{bb.zmax:.4f}]")
    
        # After 90° rotation around Y: original Z-axis → X-axis
        # So the cylinder height (0.1) is now along X, diameter (1.5) in Y and Z
        assert abs(bb.xlen - height) < TOL, f"X extent (height after Y-rotation): expected {height}, got {bb.xlen:.4f}"
        assert abs(bb.ylen - main_diameter) < TOL, f"Y extent (diameter): expected {main_diameter}, got {bb.ylen:.4f}"
        assert abs(bb.zlen - main_diameter) < TOL, f"Z extent (diameter): expected {main_diameter}, got {bb.zlen:.4f}"
    
        # Check centering: bounding box center should be at origin
        bb_cx = (bb.xmin + bb.xmax) / 2.0
        bb_cy = (bb.ymin + bb.ymax) / 2.0
        bb_cz = (bb.zmin + bb.zmax) / 2.0
        assert abs(bb_cx) < TOL, f"Center X: expected 0, got {bb_cx:.4f}"
        assert abs(bb_cy) < TOL, f"Center Y: expected 0, got {bb_cy:.4f}"
        assert abs(bb_cz) < TOL, f"Center Z: expected 0, got {bb_cz:.4f}"
    
        # Volume check: main cylinder minus 4 holes
        main_vol = math.pi * (main_radius ** 2) * height
        hole_vol = 4 * math.pi * (hole_radius ** 2) * height
        expected_vol = main_vol - hole_vol
        actual_vol = result.val().Volume()
        print(f"Expected volume: {expected_vol:.6f}, Actual volume: {actual_vol:.6f}")
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces: 1 outer cylinder + 4 hole cylinders = 5
        cyl_faces = result.faces("%Cylinder").size()
        print(f"Cylindrical faces: {cyl_faces}")
        assert cyl_faces == 5, f"Cylindrical faces: expected 5, got {cyl_faces}"
    
        # Check that the part has exactly 1 solid
        n_solids = result.solids().size()
        assert n_solids == 1, f"Number of solids: expected 1, got {n_solids}"
    
        # Check holes exist: line along X through hole positions should intersect faces
        # After 90° Y-rotation, holes are in the YZ plane
        # A hole at (offset, offset) in original XY → after 45° Z-rot → at (0, offset*sqrt(2))
        # After 90° Y-rot → at (0, offset*sqrt(2), 0) in new coords... 
        # Let's just verify the shape is inside at center
        center_point = (0, 0, 0)
        assert result.val().isInside(center_point), "Center point should be inside the solid"
    
        # Verify a point at a hole location is NOT inside the solid
        # After all rotations, one hole should be along +Y or +Z axis
        # Original hole at (offset, offset) after 45° Z-rot → (0, offset*sqrt(2), 0)
        # After 90° Y-rot: (x,y,z) → (z, y, -x), so (0, offset*sqrt(2), 0) → (0, offset*sqrt(2), 0)
        hole_y = offset * math.sqrt(2)
        hole_check = (0, hole_y, 0)
        print(f"Checking hole at: {hole_check}")
        # This point should be inside the hole (not inside solid material)
        assert not result.val().isInside(hole_check), \
            f"Point {hole_check} should be inside a hole (not solid material)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00034243/gpt_generated.stl')
