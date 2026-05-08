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
        length = 100.0   # long dimension (X)
        width  = 30.0    # short dimension (Y)
        height = 10.0    # extrusion height
        R      = 8.0     # fillet radius for two corners on one long edge (+Y side)
    
        # Half dimensions
        hl = length / 2   # 50
        hw = width  / 2   # 15
    
        # --- Step 1 & 2: Draw closed profile manually using lines and arcs ---
        # Profile traced counter-clockwise starting from bottom-left:
        #   Bottom-left (-hl, -hw) -> Bottom-right (hl, -hw): straight bottom
        #   Bottom-right (hl, -hw) -> (hl, hw-R): straight right side
        #   Arc: (hl, hw-R) -> (hl-R, hw): top-right quarter-circle fillet
        #   (hl-R, hw) -> (-hl+R, hw): straight top
        #   Arc: (-hl+R, hw) -> (-hl, hw-R): top-left quarter-circle fillet
        #   (-hl, hw-R) -> (-hl, -hw): straight left side
        #   close back to start
    
        # Arc midpoints (point on arc at 45 degrees from center):
        # Top-right arc center: (hl-R, hw-R)
        # Midpoint at 45°: (hl-R + R*cos(45°), hw-R + R*sin(45°))
        sq2 = math.sqrt(2)
        tr_mid_x =  hl - R + R / sq2
        tr_mid_y =  hw - R + R / sq2
    
        # Top-left arc center: (-hl+R, hw-R)
        # Midpoint at 135°: (-hl+R + R*cos(135°), hw-R + R*sin(135°))
        tl_mid_x = -hl + R - R / sq2
        tl_mid_y =  hw - R + R / sq2
    
        result = (
            cq.Workplane("XY")
            .moveTo(-hl, -hw)                    # start: bottom-left
            .lineTo( hl, -hw)                    # bottom edge (straight)
            .lineTo( hl,  hw - R)               # right side up to fillet tangent
            .threePointArc((tr_mid_x, tr_mid_y), (hl - R, hw))   # top-right fillet arc
            .lineTo(-hl + R, hw)                 # top edge (straight)
            .threePointArc((tl_mid_x, tl_mid_y), (-hl, hw - R))  # top-left fillet arc
            .lineTo(-hl, -hw)                    # left side down
            .close()
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 0.5
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # The object should be centered at origin in X and Y
        cx = (bb.xmax + bb.xmin) / 2
        cy = (bb.ymax + bb.ymin) / 2
        assert abs(cx) < TOL, f"Center X: expected 0, got {cx}"
        assert abs(cy) < TOL, f"Center Y: expected 0, got {cy}"
    
        # Volume: rectangle minus two quarter-circle corner cutouts
        rect_vol     = length * width * height
        corner_area  = R**2 - math.pi * R**2 / 4   # square corner minus quarter circle
        corner_vol   = 2 * corner_area * height
        expected_vol = rect_vol - corner_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count:
        # 1 bottom flat face
        # 1 top flat face
        # 1 bottom long edge face (straight, -Y side)
        # 1 top long edge face (straight, +Y side, between the two fillets)
        # 1 left short side face (straight, -X side, below fillet)
        # 1 right short side face (straight, +X side, below fillet)
        # 2 cylindrical fillet faces
        # Total: 8 faces
        face_count = result.faces().size()
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        # Two cylindrical faces (the fillets)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Bottom at z=0, top at z=height
        assert abs(bb.zmin) < TOL,          f"Bottom Z: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"Top Z: expected {height}, got {bb.zmax}"
    
        # Filleted corners are on +Y side: ymax should equal hw
        assert abs(bb.ymax - hw) < TOL,   f"Y max: expected {hw}, got {bb.ymax}"
        # Sharp bottom edge: ymin should equal -hw
        assert abs(bb.ymin - (-hw)) < TOL, f"Y min: expected {-hw}, got {bb.ymin}"
    
        # Verify the solid contains a point in the center
        center_point = (0, 0, height / 2)
        assert result.val().isInside(center_point), \
            f"Center point {center_point} should be inside the solid"
    
        # Verify sharp corners exist at bottom (no fillet there)
        # Point just inside bottom-right corner should be inside solid
        br_inside = (hl - 0.5, -hw + 0.5, height / 2)
        assert result.val().isInside(br_inside), \
            f"Bottom-right corner interior point should be inside solid"
    
        # Verify filleted corners: point at exact top-right corner should be outside
        tr_outside = (hl - 0.1, hw - 0.1, height / 2)
        assert not result.val().isInside(tr_outside), \
            f"Top-right corner point {tr_outside} should be outside (filleted)"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"  Faces: {face_count}, Cylindrical: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997681/gpt_generated.stl')
