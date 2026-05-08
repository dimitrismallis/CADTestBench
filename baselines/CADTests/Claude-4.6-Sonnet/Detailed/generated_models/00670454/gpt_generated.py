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
        length = 1.125      # X dimension
        width  = 1.5        # Y dimension
        height = 0.039474   # Z dimension (extrusion)
        hole_diameter = 0.059211
        hole_radius   = hole_diameter / 2.0
        inset_length  = 0.108553   # inset from left/right edge (X direction)
        inset_width   = 0.098684   # inset from top/bottom edge (Y direction)
    
        # --- Step 1: Create the base rectangular box ---
        # Centered at origin: X from -0.5625 to +0.5625, Y from -0.75 to +0.75, Z from -height/2 to +height/2
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Compute hole positions ---
        # Left side: X = -length/2 + inset_length
        hole_x = -length / 2.0 + inset_length   # = -0.5625 + 0.108553 = -0.453947
        # Top hole: Y = +width/2 - inset_width
        hole_y_top    = +width / 2.0 - inset_width  # = 0.75 - 0.098684 = 0.651316
        # Bottom hole: Y = -width/2 + inset_width
        hole_y_bottom = -width / 2.0 + inset_width  # = -0.75 + 0.098684 = -0.651316
    
        # --- Step 3: Add two through-holes on the left side (top and bottom) ---
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(hole_x, hole_y_top), (hole_x, hole_y_bottom)])
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Bounding box extents — box is centered at origin
        assert abs(bb.xmin - (-length/2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - (+length/2)) < TOL, f"xmax: expected {+length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width/2))  < TOL, f"ymin: expected {-width/2}, got {bb.ymin}"
        assert abs(bb.ymax - (+width/2))  < TOL, f"ymax: expected {+width/2}, got {bb.ymax}"
        assert abs(bb.zmin - (-height/2)) < TOL, f"zmin: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - (+height/2)) < TOL, f"zmax: expected {+height/2}, got {bb.zmax}"
    
        # Volume check: box minus two cylindrical holes
        box_vol  = length * width * height
        hole_vol = 2 * math.pi * hole_radius**2 * height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Cylindrical faces: 2 holes → 2 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Circular edges: each hole has 2 circular edges (top + bottom) → 4 total
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 4, f"Circular edges: expected 4, got {circ_edges}"
    
        # Verify holes exist using isInside:
        # The center of each hole should NOT be inside the solid (it's empty space)
        shape = result.val()
        z_mid = 0.0  # midplane of the centered box
    
        top_hole_center = cq.Vector(hole_x, hole_y_top, z_mid)
        assert not shape.isInside(top_hole_center), \
            f"Top hole center should be empty (not inside solid), but isInside returned True"
    
        bot_hole_center = cq.Vector(hole_x, hole_y_bottom, z_mid)
        assert not shape.isInside(bot_hole_center), \
            f"Bottom hole center should be empty (not inside solid), but isInside returned True"
    
        # A point well inside the solid (away from holes) should be inside
        solid_point = cq.Vector(0.0, 0.0, z_mid)
        assert shape.isInside(solid_point), \
            f"Center of box should be inside solid, but isInside returned False"
    
        # A point just outside the hole radius but at same X,Y region should be inside solid
        # Offset by 2x hole radius from hole center in Y direction
        offset_point_top = cq.Vector(hole_x, hole_y_top + hole_radius * 3, z_mid)
        assert shape.isInside(offset_point_top), \
            f"Point near (but outside) top hole should be inside solid"
    
        # Verify hole positions are inside the bounding box
        assert hole_x > bb.xmin and hole_x < bb.xmax, \
            f"Hole X={hole_x} not inside [{bb.xmin}, {bb.xmax}]"
        assert hole_y_top > bb.ymin and hole_y_top < bb.ymax, \
            f"Top hole Y={hole_y_top} not inside [{bb.ymin}, {bb.ymax}]"
        assert hole_y_bottom > bb.ymin and hole_y_bottom < bb.ymax, \
            f"Bottom hole Y={hole_y_bottom} not inside [{bb.ymin}, {bb.ymax}]"
    
        # Verify the holes are on the left side (hole_x < 0)
        assert hole_x < 0, f"Holes should be on left side (X < 0), got hole_x={hole_x}"
    
        # Verify symmetry: top and bottom holes are symmetric about Y=0
        assert abs(hole_y_top + hole_y_bottom) < TOL, \
            f"Holes not symmetric about Y=0: top={hole_y_top}, bottom={hole_y_bottom}"
    
        print("All assertions passed!")
        print(f"  Box: {length} x {width} x {height}")
        print(f"  Hole diameter: {hole_diameter}, radius: {hole_radius:.6f}")
        print(f"  Hole X position: {hole_x:.6f}")
        print(f"  Top hole Y: {hole_y_top:.6f}, Bottom hole Y: {hole_y_bottom:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670454/gpt_generated.stl')
