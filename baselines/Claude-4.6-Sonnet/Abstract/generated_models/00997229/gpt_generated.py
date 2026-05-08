import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        handle_length = 80.0   # total length of the handle rectangle
        handle_width  = 15.0   # width of the handle
        thickness     = 8.0    # extrusion depth
    
        r_small = 12.0         # radius of small circular end
        r_large = 16.0         # radius of large circular end
    
        hole_r_small = 7.0     # radius of hole in small end
        hole_r_large = 10.0    # radius of hole in large end
    
        # The circles are centered at the ends of the handle rectangle.
        # Rectangle spans from x = -handle_length/2 to x = +handle_length/2
        # Small circle at x = -handle_length/2, Large circle at x = +handle_length/2
    
        cx_small = -handle_length / 2.0   # -40
        cx_large =  handle_length / 2.0   #  +40
    
        # --- Step 1: Build the 2D profile using Sketch API ---
        # Union of: rectangle + small circle + large circle
        sketch = (
            cq.Sketch()
            # Rectangle (handle body)
            .rect(handle_length, handle_width)
            # Small circle at left end
            .push([(cx_small, 0)])
            .circle(r_small, mode="a")
            .reset()
            # Large circle at right end
            .push([(cx_large, 0)])
            .circle(r_large, mode="a")
            .reset()
        )
    
        # --- Step 2: Extrude the sketch ---
        result = cq.Workplane("XY").placeSketch(sketch).extrude(thickness)
    
        # --- Step 3: Cut hole in small circular end ---
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(cx_small, 0)])
            .hole(hole_r_small * 2)   # hole() takes diameter
        )
    
        # --- Step 4: Cut hole in large circular end ---
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(cx_large, 0)])
            .hole(hole_r_large * 2)   # hole() takes diameter
        )
    
        # --- Final object verification ---
        TOL = 0.5  # generous tolerance for complex shapes
    
        bb = result.val().BoundingBox()
    
        # Bounding box X: from cx_small - r_small to cx_large + r_large
        expected_xlen = (cx_large + r_large) - (cx_small - r_small)  # 40+16 - (-40-12) = 56+52 = 108
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
    
        # Bounding box Y: dominated by the large circle diameter
        expected_ylen = r_large * 2  # 32
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
    
        # Bounding box Z: extrusion thickness
        assert abs(bb.zlen - thickness) < TOL, \
            f"Z length (thickness): expected {thickness}, got {bb.zlen}"
    
        # Volume check: approximate
        # Profile area ≈ rect + small circle + large circle - overlaps (overlaps small)
        # Rough lower bound: just the circles + handle
        rect_area = handle_length * handle_width
        small_circle_area = math.pi * r_small**2
        large_circle_area = math.pi * r_large**2
        # Subtract holes
        small_hole_area = math.pi * hole_r_small**2
        large_hole_area = math.pi * hole_r_large**2
        # Approximate volume (ignoring overlaps between rect and circles for bound check)
        approx_vol = (rect_area + small_circle_area + large_circle_area - small_hole_area - large_hole_area) * thickness
        actual_vol = result.val().Volume()
        # Allow 30% tolerance due to overlaps
        assert actual_vol > approx_vol * 0.5, \
            f"Volume too small: expected > {approx_vol*0.5:.1f}, got {actual_vol:.1f}"
        assert actual_vol < approx_vol * 1.5, \
            f"Volume too large: expected < {approx_vol*1.5:.1f}, got {actual_vol:.1f}"
    
        # Check two cylindrical hole faces exist (the two through-holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (holes), got {cyl_faces}"
    
        # Check the holes go all the way through (points inside holes should be outside solid)
        solid = result.val()
        # Point at center of small hole, mid-thickness — should be OUTSIDE (it's a hole)
        pt_small_hole = (cx_small, 0, thickness / 2)
        assert not solid.isInside(pt_small_hole), \
            f"Small hole center should be outside solid (it's a hole), but isInside returned True"
    
        # Point at center of large hole, mid-thickness — should be OUTSIDE
        pt_large_hole = (cx_large, 0, thickness / 2)
        assert not solid.isInside(pt_large_hole), \
            f"Large hole center should be outside solid (it's a hole), but isInside returned True"
    
        # Point in the middle of the handle — should be INSIDE
        pt_handle = (0, 0, thickness / 2)
        assert solid.isInside(pt_handle), \
            f"Handle center should be inside solid, but isInside returned False"
    
        # Check the large end is bigger than the small end by checking bounding box asymmetry
        # The large circle extends further in +X than the small circle extends in -X
        large_extent = bb.xmax  # should be ~56
        small_extent = -bb.xmin  # should be ~52
        assert large_extent > small_extent, \
            f"Large end ({large_extent:.1f}) should extend further than small end ({small_extent:.1f})"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} mm³")
        print(f"Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997229/gpt_generated.stl')
