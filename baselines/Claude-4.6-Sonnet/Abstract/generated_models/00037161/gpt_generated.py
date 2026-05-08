import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        square_size = 50.0      # square side length (mm)
        square_thickness = 5.0  # thickness of the square plate
    
        rect_width = 10.0       # tiny rectangle width
        rect_height = 5.0       # tiny rectangle height
    
        # --- Step 1: Create the square plate (50x50x5 mm box) ---
        result = cq.Workplane("XY").box(square_size, square_size, square_thickness)
    
        # --- Step 2: Cut a tiny empty rectangle in the center ---
        # The box is centered at origin, so the top face workplane is at z=+2.5
        # We cut a rectangle centered at (0,0) on the top face, going through all
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(rect_width, rect_height)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check overall bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - square_size) < TOL, f"X length: expected {square_size}, got {bb.xlen}"
        assert abs(bb.ylen - square_size) < TOL, f"Y length: expected {square_size}, got {bb.ylen}"
        assert abs(bb.zlen - square_thickness) < TOL, f"Z length: expected {square_thickness}, got {bb.zlen}"
    
        # Check volume: square plate minus the rectangular cutout
        expected_vol = (square_size * square_size * square_thickness) - (rect_width * rect_height * square_thickness)
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check that the center of the solid is at origin (symmetric shape)
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Check that a point inside the rectangular cutout is NOT inside the solid
        # The cutout is centered at (0,0), so a point at (0,0,0) should be outside
        cutout_point = (0.0, 0.0, 0.0)
        assert not result.val().isInside(cutout_point), \
            f"Point {cutout_point} should be inside the cutout (not inside solid)"
    
        # Check that a point clearly inside the solid material IS inside
        # e.g., near a corner of the plate, away from the cutout
        solid_point = (20.0, 20.0, 0.0)
        assert result.val().isInside(solid_point), \
            f"Point {solid_point} should be inside the solid material"
    
        # Check that the rectangular hole exists by verifying faces intersected along Z
        # A line through the center along Z should intersect 0 faces (open hole)
        faces_through_center = result.val().facesIntersectedByLine((0, 0, -10), (0, 0, 1))
        # The hole is open, so a vertical line through center hits only the side walls of the cutout
        # but NOT the top or bottom faces (they are cut away)
        assert len(faces_through_center) == 0, \
            f"Line through cutout center should hit 0 top/bottom faces, got {len(faces_through_center)}"
    
        # Check cylindrical faces count = 0 (no circular holes, only rectangular cutout)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check planar faces: original box has 6 faces, cutout adds 4 side walls, removes top/bottom patches
        # Top face: 1 face with rectangular hole (ring shape) → still 1 planar face
        # Bottom face: same → 1 planar face
        # 4 side faces of box → 4 planar faces
        # 4 inner walls of rectangular cutout → 4 planar faces
        # Total = 10 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 10, f"Expected 10 planar faces, got {planar_faces}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00037161/gpt_generated.stl')
