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
        length = 1.08869      # X dimension
        width  = 0.870954     # Y dimension
        height = 0.108869     # Z dimension
        fillet_r = 0.217746   # fillet radius for top edges
        hole_dia = 0.195965   # hole diameter
        hole_r   = hole_dia / 2.0  # 0.097983
        hole_offset_from_left = 0.228625  # X offset from left edge
    
        # Derived positions (box centered at origin)
        left_edge_x  = -length / 2.0   # -0.544345
        top_edge_y   =  width  / 2.0   #  0.435477
    
        hole_x = left_edge_x + hole_offset_from_left  # -0.31572
        hole_y = top_edge_y - hole_r                   #  0.337494
    
        # --- Step 1: Create base rectangle extruded to height ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Fillet the top corners (vertical edges at max Y side) ---
        # Select the 2 vertical edges (parallel to Z) at the top (max Y) corners
        # These are the edges at the top of the tag shape
        result = result.edges("|Z").edges(">Y").fillet(fillet_r)
    
        # --- Step 3: Add circular through-hole ---
        # Position: X = left_edge + offset, Y = just below top edge
        result = (
            result
            .faces(">Z").workplane()
            .center(hole_x, hole_y)
            .hole(hole_dia)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box: X and Z unchanged by fillet (fillet is on vertical edges at top)
        # Y is unchanged (fillet rounds corners, doesn't reduce bounding box in Y)
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check: box - fillet material removed - hole
        # Approximate: box volume minus hole volume (fillet volume is complex to compute exactly)
        box_vol  = length * width * height
        hole_vol = math.pi * hole_r**2 * height
        # Fillet removes 4 quarter-cylinders at the 2 top vertical edges (each edge has height=height)
        # Each fillet is a quarter-cylinder of radius fillet_r and height height
        # But fillet_r = 0.217746 > width/2 = 0.435477... wait, fillet_r = 0.217746 < width/2 = 0.435477
        # Two vertical edges at top corners, each gets a quarter-cylinder removed
        fillet_vol = 2 * (fillet_r**2 - math.pi * fillet_r**2 / 4) * height  # square corner minus quarter circle
        expected_vol = box_vol - fillet_vol - hole_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces exist (hole + 2 fillet surfaces)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # Check hole exists: a line through the hole center should intersect faces on both sides
        hole_center_3d = (hole_x, hole_y, 0)
        faces_hit = solid.facesIntersectedByLine(hole_center_3d, (0, 0, 1))
        assert len(faces_hit) == 0, \
            f"Line through hole center should pass through empty space (0 face hits), got {len(faces_hit)}"
    
        # Check the hole is present by verifying the point inside the hole is NOT inside the solid
        hole_interior_pt = (hole_x, hole_y, height / 2.0)
        assert not solid.isInside(hole_interior_pt), \
            f"Point inside hole should NOT be inside solid: {hole_interior_pt}"
    
        # Check a point in the solid body IS inside
        body_pt = (0.0, 0.0, height / 2.0)
        assert solid.isInside(body_pt), \
            f"Point in body should be inside solid: {body_pt}"
    
        # Check center of mass is roughly centered in X (symmetric about X=0 after fillet)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < 0.05, f"Center of mass X should be near 0, got {com.x}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670266/gpt_generated.stl')
