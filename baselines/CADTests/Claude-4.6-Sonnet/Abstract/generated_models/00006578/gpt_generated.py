import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length   = 80.0   # X dimension
        width    = 60.0   # Y dimension
        height   = 5.0    # Z dimension (thickness)
        hole_d   = 6.0    # hole diameter
        margin   = 10.0   # distance from each edge to hole center
    
        # --- Step 1: Create the base rectangular plate ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Create four corner holes (through-holes) ---
        # Hole centers at (±(length/2 - margin), ±(width/2 - margin))
        hx = length / 2 - margin   # 30.0
        hy = width  / 2 - margin   # 20.0
    
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([
                ( hx,  hy),   # near top-right corner
                (-hx,  hy),   # near top-left corner
                ( hx, -hy),   # near bottom-right corner
                (-hx, -hy),   # near bottom-left corner
            ])
            .hole(hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # 2. Volume: plate minus four cylindrical holes
        plate_vol = length * width * height
        hole_vol  = 4 * math.pi * (hole_d / 2) ** 2 * height
        expected_vol = plate_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, (
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
        )
    
        # 3. Four cylindrical faces (one per hole)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 4, (
            f"Cylindrical faces: expected 4 (one per hole), got {cyl_face_count}"
        )
    
        # 4. Circular edges: each hole has 2 circular edges (top + bottom) → 8 total
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 8, (
            f"Circular edges: expected 8 (2 per hole × 4 holes), got {circ_edge_count}"
        )
    
        # 5. Hole void and plate material checks
        solid = result.val()
        hx_c = length / 2 - margin   # 30.0
        hy_c = width  / 2 - margin   # 20.0
    
        hole_centers = [( hx_c,  hy_c), (-hx_c,  hy_c), ( hx_c, -hy_c), (-hx_c, -hy_c)]
    
        for (cx, cy) in hole_centers:
            # Point at hole center → should be OUTSIDE solid (inside the hole void)
            pt_in_hole = (cx, cy, 0)
            assert not solid.isInside(pt_in_hole), (
                f"Point {pt_in_hole} should NOT be inside the solid (it's in the hole)"
            )
    
            # Point between hole edge and plate corner → should be INSIDE solid (plate material)
            # margin=10mm, hole_radius=3mm → 7mm of material toward the corner from hole center
            # Step 5mm toward the corner (well within plate material)
            sign_x = 1.0 if cx > 0 else -1.0
            sign_y = 1.0 if cy > 0 else -1.0
            pt_material = (cx + sign_x * 5.0, cy + sign_y * 5.0, 0)
            assert solid.isInside(pt_material), (
                f"Point {pt_material} should be inside the solid (plate material near corner)"
            )
    
            # Point between hole center and plate center → also plate material
            pt_center_side = (cx - sign_x * 5.0, cy - sign_y * 5.0, 0)
            assert solid.isInside(pt_center_side), (
                f"Point {pt_center_side} should be inside the solid (plate material toward center)"
            )
    
        # 6. Symmetry: box is centered at origin, so CoM should be at (0, 0, 0)
        # box() centers by default → spans Z from -height/2 to +height/2
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"CoM Z: expected 0 (box centered at origin), got {com.z}"
    
        # 7. Bounding box Z spans from -height/2 to +height/2
        assert abs(bb.zmin - (-height / 2)) < TOL, f"Z min: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - ( height / 2)) < TOL, f"Z max: expected { height/2}, got {bb.zmax}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00006578/gpt_generated.stl')
