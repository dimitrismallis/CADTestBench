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
        side      = 20.0   # square side length (mm)
        thickness =  2.0   # slight extrusion height (mm)
        hole_d    =  1.0   # very small hole diameter (mm)
        hole_r    =  hole_d / 2.0
    
        # --- Step 1: Draw a square and extrude it slightly ---
        result = (
            cq.Workplane("XY")
            .rect(side, side)
            .extrude(thickness)
        )
    
        # --- Step 2: Create a very small hole in the center ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .hole(hole_d)          # centered on workplane origin = center of top face
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2a. Bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - side)      < TOL, f"X length: expected {side}, got {bb.xlen}"
        assert abs(bb.ylen - side)      < TOL, f"Y length: expected {side}, got {bb.ylen}"
        assert abs(bb.zlen - thickness) < TOL, f"Z length: expected {thickness}, got {bb.zlen}"
    
        # 2b. Volume: box minus cylindrical hole
        box_vol  = side * side * thickness
        hole_vol = math.pi * hole_r**2 * thickness
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, (
            f"Volume: expected ~{expected_vol:.4f}, got {actual_vol:.4f}"
        )
    
        # 2c. Cylindrical face count: exactly 1 (the hole wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # 2d. Planar face count: 6 (top, bottom, 4 sides) — hole adds 0 planar faces
        plane_faces = result.faces("%Plane").size()
        assert plane_faces == 6, f"Planar faces: expected 6, got {plane_faces}"
    
        # 2e. Hole is present at center: a point just inside the hole should NOT be inside the solid
        center_in_hole = (0.0, 0.0, thickness / 2.0)   # dead center of the hole
        assert not result.val().isInside(center_in_hole), (
            "Center of hole should be outside (empty) the solid, but isInside returned True"
        )
    
        # 2f. A point well inside the solid (away from hole) should be inside
        solid_point = (side * 0.4, side * 0.4, thickness / 2.0)
        assert result.val().isInside(solid_point), (
            f"Point {solid_point} should be inside the solid, but isInside returned False"
        )
    
        # 2g. Circular edges: 2 (top rim + bottom rim of the hole)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, f"Circular edges: expected 2, got {circ_edges}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00672804/gpt_generated.stl')
