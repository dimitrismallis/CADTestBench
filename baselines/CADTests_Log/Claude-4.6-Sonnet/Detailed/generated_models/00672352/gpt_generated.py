import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 0.75
        width = 0.375
        height = 0.015611
        hole_diameter = 0.09375
        hole_radius = hole_diameter / 2  # 0.046875
        padding = 0.015625
    
        # --- Step 1: Create the rectangular box ---
        # Box is centered at origin by default
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Position the hole in the top right corner ---
        # Box extends from -length/2 to +length/2 in X
        # Box extends from -width/2 to +width/2 in Y
        # Right edge at x = length/2 = 0.375
        # Top edge at y = width/2 = 0.1875
        # Hole center: x = length/2 - padding - hole_radius
        #              y = width/2 - padding - hole_radius
        hole_x = length / 2 - padding - hole_radius   # 0.375 - 0.015625 - 0.046875 = 0.3125
        hole_y = width / 2 - padding - hole_radius     # 0.1875 - 0.015625 - 0.046875 = 0.125
    
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(hole_x, hole_y)
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check: box volume minus cylinder volume
        box_vol = length * width * height
        hole_vol = math.pi * hole_radius**2 * height
        expected_vol = box_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical face exists (the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # Check circular edges exist (top and bottom rim of hole)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges >= 2, f"Expected at least 2 circular edges (top and bottom of hole), got {circ_edges}"
    
        solid = result.val()
    
        # Check hole position: the center of the hole at mid-height should NOT be inside the solid
        # Box is centered at z=0, so mid-height is z=0
        point_in_hole = (hole_x, hole_y, 0.0)
        assert not solid.isInside(point_in_hole, tolerance=1e-5), \
            f"Point {point_in_hole} should be inside the hole (not solid), but isInside returned True"
    
        # A point at the center of the box should be inside the solid
        point_in_solid = (0.0, 0.0, 0.0)
        assert solid.isInside(point_in_solid, tolerance=1e-5), \
            f"Point {point_in_solid} should be inside the solid, but isInside returned False"
    
        # A point just outside the hole radius (toward center of box) should be inside the solid
        # Move slightly inward from hole edge toward box center
        offset = hole_radius * 1.5  # just outside the hole radius from hole center, toward box center
        point_near_hole_outside = (hole_x - offset, hole_y, 0.0)
        assert solid.isInside(point_near_hole_outside, tolerance=1e-5), \
            f"Point {point_near_hole_outside} should be inside the solid (outside hole), but isInside returned False"
    
        # Check hole is a through-hole: line through hole center along Z should intersect
        # the cylindrical wall face (not the planar faces which have the hole cut out)
        # Verify by checking that a point just inside the hole radius is NOT in the solid
        point_inside_hole_radius = (hole_x + hole_radius * 0.5, hole_y, 0.0)
        assert not solid.isInside(point_inside_hole_radius, tolerance=1e-5), \
            f"Point {point_inside_hole_radius} should be inside the hole void, but isInside returned True"
    
        # Check hole diameter via circular edge radius
        circ_edge_list = result.edges("%Circle").vals()
        # Find the circular edges that correspond to the hole (should have radius = hole_radius)
        hole_edges = [e for e in circ_edge_list if abs(e.radius() - hole_radius) < TOL]
        assert len(hole_edges) >= 2, \
            f"Expected at least 2 circular edges with radius {hole_radius:.6f}, found {len(hole_edges)}"
    
        print("All assertions passed!")
        print(f"  Box: {length} x {width} x {height}")
        print(f"  Hole diameter: {hole_diameter}, at ({hole_x:.6f}, {hole_y:.6f})")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00672352/gpt_generated.stl')
