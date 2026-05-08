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
        box_length = 80.0   # X dimension (longer)
        box_width  = 40.0   # Y dimension (shorter edges are at ±X = ±40)
        box_height = 20.0   # Z dimension
        hole_radius = 8.0   # circular hole radius
        slit_width  = 0.5   # thin slit width (wire-cutter style)
    
        # --- Step 1: Create the rectangular block ---
        result = cq.Workplane("XY").box(box_length, box_width, box_height)
    
        # --- Step 2: Create circular hole at midpoint of rectangle (center), going through full height ---
        # The midpoint of the rectangle is at (0, 0). We drill from the top face downward.
        result = (
            result
            .faces(">Z").workplane()
            .circle(hole_radius)
            .cutThruAll()
        )
    
        # --- Step 3: Create thin slit from the top of the circular hole to the shorter edge ---
        # The shorter edges are the faces perpendicular to X (at x = ±40).
        # We cut a slit from the circle edge (x = hole_radius) to the +X face (x = box_length/2).
        # The slit is thin in Y (slit_width), full height in Z, and spans from circle edge to short face.
        # We use a box cutter positioned to cover that span.
    
        # Slit cutter: 
        #   X: from hole_radius to box_length/2  → length = box_length/2 - hole_radius, centered at midpoint
        #   Y: slit_width (very thin)
        #   Z: box_height (full height)
        slit_x_start = hole_radius
        slit_x_end   = box_length / 2.0
        slit_x_len   = slit_x_end - slit_x_start
        slit_x_center = (slit_x_start + slit_x_end) / 2.0
    
        slit_cutter = (
            cq.Workplane("XY")
            .box(slit_x_len, slit_width, box_height, centered=True)
            .translate((slit_x_center, 0, 0))
        )
    
        result = result.cut(slit_cutter)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box: should still be 80 × 40 × 20
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - box_length) < TOL, f"X length: expected {box_length}, got {bb.xlen}"
        assert abs(bb.ylen - box_width)  < TOL, f"Y length: expected {box_width}, got {bb.ylen}"
        assert abs(bb.zlen - box_height) < TOL, f"Z length: expected {box_height}, got {bb.zlen}"
    
        # 2. Volume check: box minus cylinder minus slit box (approximate)
        box_vol    = box_length * box_width * box_height
        hole_vol   = math.pi * hole_radius**2 * box_height
        # Slit volume: thin rectangle minus the part that overlaps the hole
        # The slit starts at x=hole_radius, so no overlap with hole (hole is a circle, slit starts at its edge)
        slit_vol   = slit_x_len * slit_width * box_height
        expected_vol = box_vol - hole_vol - slit_vol
        actual_vol   = result.val().Volume()
        # Allow 5% tolerance due to slit/hole boundary interaction
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # 3. Cylindrical face exists (from the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # 4. Check that the hole goes through: a point at center (0,0,0) should NOT be inside the solid
        center_point = (0.0, 0.0, 0.0)
        assert not result.val().isInside(center_point), \
            "Center point (0,0,0) should be inside the hole, not the solid"
    
        # 5. Check that a point in the slit region is NOT inside the solid
        slit_test_point = (slit_x_center, 0.0, 0.0)
        assert not result.val().isInside(slit_test_point), \
            f"Point in slit {slit_test_point} should not be inside the solid"
    
        # 6. Check that a point clearly inside the solid IS inside
        solid_test_point = (0.0, 15.0, 0.0)  # away from hole and slit
        assert result.val().isInside(solid_test_point), \
            f"Point {solid_test_point} should be inside the solid"
    
        # 7. Check that the slit reaches the shorter edge (face at x = +40)
        # A point just inside the +X face, in the slit, should be outside the solid
        near_edge_slit = (box_length/2 - 0.5, 0.0, 0.0)
        assert not result.val().isInside(near_edge_slit), \
            f"Point near +X edge in slit {near_edge_slit} should not be inside the solid"
    
        # 8. Planar faces count: box has 6 faces, hole adds 2 circular caps (top/bottom),
        #    slit adds planar faces. At minimum we expect more than 6 planar faces.
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 6, f"Expected at least 6 planar faces, got {planar_faces}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00034100/gpt_generated.stl')
