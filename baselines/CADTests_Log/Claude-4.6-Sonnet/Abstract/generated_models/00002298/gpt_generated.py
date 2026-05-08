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
        base_length = 80.0   # X dimension
        base_width  = 40.0   # Y dimension
        base_height = 5.0    # Z dimension (slight extrusion)
    
        cut_length  = 20.0   # X dimension of cut-out
        cut_width   = 40.0   # Y dimension (full width, through all)
        cut_height  = 2.0    # Z dimension of cut-out
    
        # Base box is centered at origin: X in [-40,40], Y in [-20,20], Z in [-2.5, 2.5]
        # Midpoint of height in absolute terms (from bottom) = base_height/2 = 2.5
        # "Slightly above midpoint" → cut-out bottom at Z_abs = 3.0 from bottom
        # In centered coords: Z_abs - base_height/2 = 3.0 - 2.5 = 0.5
        # Cut-out occupies Z: [0.5, 2.5] in centered coords (height = 2.0)
        # Cut-out center Z in centered coords = 0.5 + 1.0 = 1.5
    
        cut_center_z_centered = 1.5  # center of cut in centered coords
    
        # --- Step 1: Create the base rectangle extruded slightly ---
        base = cq.Workplane("XY").box(base_length, base_width, base_height)
    
        # Debug: check base volume
        base_vol_actual = base.val().Volume()
        base_vol_expected = base_length * base_width * base_height
        print(f"Base volume: actual={base_vol_actual:.2f}, expected={base_vol_expected:.2f}")
    
        # --- Step 2: Create the rectangular cut-out using a workplane approach ---
        # Use the top face workplane and cut downward
        # Cut-out: 20 wide (X), full width (Y=40), 2 deep (Z)
        # Positioned at X=0 (midpoint of length), slightly above midpoint of height
        # "Slightly above midpoint" means the cut starts at Z=0.5 (centered) = 3.0 from bottom
        # We cut from Z=2.5 (top) downward by cut_height=2.0, reaching Z=0.5
        # This places the cut from Z=0.5 to Z=2.5 in centered coords ✓
    
        result = (
            base
            .faces(">Z").workplane()          # workplane at top face (Z=2.5)
            .center(0, 0)                      # center at X=0, Y=0 (midpoint of length)
            .rect(cut_length, cut_width)       # 20 x 40 rectangle
            .cutBlind(-cut_height)             # cut downward by 2mm
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box: overall dimensions should still be 80 x 40 x 5
        bb = result.val().BoundingBox()
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        assert abs(bb.xlen - base_length) < TOL, f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - base_width)  < TOL, f"Y width: expected {base_width}, got {bb.ylen}"
        assert abs(bb.zlen - base_height) < TOL, f"Z height: expected {base_height}, got {bb.zlen}"
    
        # 2. Volume: base volume minus cut-out volume
        base_vol  = base_length * base_width * base_height   # 16000
        cut_vol   = cut_length * cut_width * cut_height       # 1600
        expected_vol = base_vol - cut_vol                     # 14400
        actual_vol = result.val().Volume()
        print(f"Volume: actual={actual_vol:.2f}, expected={expected_vol:.2f}")
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Symmetry: cut-out is centered at X=0 (midpoint of length)
        com = cq.Shape.centerOfMass(result.val())
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
        assert abs(com.x) < TOL, f"Center of mass X should be ~0 (symmetric), got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0 (symmetric), got {com.y}"
    
        # 4. The cut-out is slightly above midpoint of height
        # In centered coords, midpoint of height = 0.0
        # Cut-out occupies Z: [0.5, 2.5], so material removed from upper portion
        # COM Z should be slightly below 0 (shifted downward)
        assert com.z < 0.0, f"Center of mass Z should be below 0 (cut above midpoint), got {com.z}"
    
        # 5. Point inside the cut-out region should be OUTSIDE the solid
        # Cut region: X in [-10,10], Y in [-20,20], Z in [0.5, 2.5] (centered coords)
        cut_interior = (0.0, 0.0, 1.5)
        assert not result.val().isInside(cut_interior), \
            f"Point {cut_interior} should be outside (in cut-out), but is inside"
    
        # 6. Point below the cut (in solid region) should be INSIDE
        solid_point = (0.0, 0.0, -1.0)
        assert result.val().isInside(solid_point), \
            f"Point {solid_point} should be inside the solid, but is outside"
    
        # 7. Point outside the base should be OUTSIDE
        outside_point = (50.0, 0.0, 0.0)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside the solid"
    
        # 8. Point in base but outside cut-out X range should be INSIDE
        side_point = (35.0, 0.0, 1.5)  # X=35 is outside cut (cut only covers X in [-10,10])
        assert result.val().isInside(side_point), \
            f"Point {side_point} should be inside (outside cut X range), but is outside"
    
        # 9. No cylindrical faces (all cuts are rectangular)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # 10. Check face count: base box has 6 faces; cut adds faces
        # The cut-out on top creates: removes part of top face, adds 3 new faces (bottom + 2 sides in X)
        # Y sides of cut coincide with Y sides of base → no new Y faces
        # Expected faces: 6 (base) - 1 (top removed) + 1 (top remaining, now 2 parts = 2 faces)
        #                 + 1 (cut bottom) + 2 (cut X walls) = 10 faces
        # Actually: top face split into 2 parts + cut bottom + 2 X-walls = 6-1+2+1+2 = 10
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count == 10, f"Expected 10 faces, got {face_count}"
    
        print("All assertions passed!")
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00002298/gpt_generated.stl')
