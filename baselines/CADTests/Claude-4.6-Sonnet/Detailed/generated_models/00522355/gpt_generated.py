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
        height = 0.75
        outer_diameter = 0.533654
        wall_thickness = 0.017308
        small_hole_diameter = 0.090144
        small_hole_depth = 0.034616
    
        outer_radius = outer_diameter / 2.0           # 0.266827
        inner_radius = outer_radius - wall_thickness  # 0.249519
        small_hole_radius = small_hole_diameter / 2.0 # 0.045072
    
        # Bottom plate thickness must be strictly greater than small hole depth
        bottom_plate_thickness = small_hole_depth * 2.0  # 0.069232
    
        # --- Build the entire shape as a revolved 2D profile ---
        # Profile in the XZ plane (X = radial, Z = axial):
        # The profile describes the cross-section of the solid when revolved 360° around Z.
        #
        # Shape description (cross-section, right half):
        #   - Outer wall: from (outer_r, 0) up to (outer_r, height)
        #   - Top annular face: from (outer_r, height) to (inner_r, height)
        #   - Inner wall: from (inner_r, height) down to (inner_r, bottom_plate_thickness)
        #   - Bottom plate top: from (inner_r, bottom_plate_thickness) to (small_hole_r, bottom_plate_thickness)
        #   - Small hole wall: from (small_hole_r, bottom_plate_thickness) down to (small_hole_r, 0)
        #   - Bottom face inner: from (small_hole_r, 0) to (0, 0)  [but we need hole open at bottom]
        #
        # Wait - the small hole is open at the BOTTOM (z=0) and blind at top (z=small_hole_depth).
        # So the profile should be:
        #   Start at (0, 0) - center bottom
        #   Go to (small_hole_r, 0) - bottom face inner edge of hole
        #   Go up to (small_hole_r, small_hole_depth) - hole wall
        #   Go to (inner_r, small_hole_depth) - bottom plate at hole depth level... 
        #
        # Actually let me reconsider. The bottom plate goes from z=0 to z=bottom_plate_thickness.
        # The small hole is cut from z=0 upward to z=small_hole_depth.
        # So the solid bottom plate region (in cross-section) is:
        #   - From r=small_hole_r to r=inner_r, z=0 to z=bottom_plate_thickness (annular plate)
        #   - From r=0 to r=small_hole_r, z=small_hole_depth to z=bottom_plate_thickness (plug below hole)
        #
        # Full profile (closed polygon, revolved around Z axis):
        # Points going around the cross-section:
        #   (small_hole_r, 0)          -> bottom of hole opening
        #   (small_hole_r, small_hole_depth)  -> top of hole (blind end)
        #   (0, small_hole_depth)      -> center at blind end
        #   ... no, revolution around Z means we only need the right half profile
        #
        # Let me use a simpler closed wire profile:
    
        pts = [
            (small_hole_radius, 0),                    # P1: bottom, inner edge of hole
            (inner_radius, 0),                          # P2: bottom, outer edge of plate
            (outer_radius, 0),                          # P3: bottom, outer edge of cylinder
            (outer_radius, height),                     # P4: top, outer edge
            (inner_radius, height),                     # P5: top, inner edge
            (inner_radius, bottom_plate_thickness),     # P6: top of bottom plate, inner edge
            (small_hole_radius, bottom_plate_thickness),# P7: top of hole (blind end)
            (small_hole_radius, 0),                     # back to P1
        ]
    
        # Build the profile as a closed wire in the XZ plane and revolve around Z
        result = (
            cq.Workplane("XZ")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .lineTo(pts[6][0], pts[6][1])
            .close()
            .revolve(360, (0, 0, 0), (0, 0, 1))
        )
    
        # --- Final object verification ---
        TOL = 1e-3
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - outer_diameter) < TOL, \
            f"X extent: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, \
            f"Y extent: expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # Z bounds
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"Z max: expected {height}, got {bb.zmax}"
    
        # Volume check:
        # Full outer cylinder volume
        full_outer_vol = math.pi * outer_radius**2 * height
        # Inner cavity volume (above bottom plate)
        inner_cavity_vol = math.pi * inner_radius**2 * (height - bottom_plate_thickness)
        # Small hole volume
        small_hole_vol = math.pi * small_hole_radius**2 * small_hole_depth
        expected_vol = full_outer_vol - inner_cavity_vol - small_hole_vol
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces: outer wall, inner wall, small hole wall = 3
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 3, \
            f"Expected at least 3 cylindrical faces (outer, inner, small hole), got {cyl_faces}"
    
        solid_shape = result.val()
    
        # Check the small hole: center at half hole depth should be outside solid
        hole_test_point = (0.0, 0.0, small_hole_depth / 2.0)
        assert not solid_shape.isInside(hole_test_point), \
            f"Point {hole_test_point} should be in the small hole (outside solid)"
    
        # Check tube wall is inside solid
        wall_mid_r = (outer_radius + inner_radius) / 2.0
        wall_test_point = (wall_mid_r, 0.0, height / 2.0)
        assert solid_shape.isInside(wall_test_point), \
            f"Point {wall_test_point} should be inside the tube wall"
    
        # Check inner cavity (above bottom plate) is outside solid
        inner_test_point = (0.0, 0.0, bottom_plate_thickness + (height - bottom_plate_thickness) / 2.0)
        assert not solid_shape.isInside(inner_test_point), \
            f"Point {inner_test_point} should be in the inner cavity (outside solid)"
    
        # Check bottom plate (outside small hole) is inside solid
        plate_test_r = (small_hole_radius + inner_radius) / 2.0
        plate_test_point = (plate_test_r, 0.0, small_hole_depth / 2.0)
        assert solid_shape.isInside(plate_test_point), \
            f"Point {plate_test_point} should be inside the bottom plate"
    
        # Check solid below blind hole is inside solid
        below_hole_point = (0.0, 0.0, small_hole_depth + (bottom_plate_thickness - small_hole_depth) / 2.0)
        assert solid_shape.isInside(below_hole_point), \
            f"Point {below_hole_point} should be inside solid below the blind hole"
    
        print(f"All assertions passed!")
        print(f"  Outer diameter: {outer_diameter}, Wall thickness: {wall_thickness}")
        print(f"  Height: {height}, Small hole diameter: {small_hole_diameter}, depth: {small_hole_depth}")
        print(f"  Bottom plate thickness: {bottom_plate_thickness}")
        print(f"  Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00522355/gpt_generated.stl')
