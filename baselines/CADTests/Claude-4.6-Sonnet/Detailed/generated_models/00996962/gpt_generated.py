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
        plate_length = 1.5          # X dimension
        plate_width  = 1.37143      # Y dimension
        plate_height = 0.078171     # Z dimension
    
        groove_length = 0.085714    # X dimension of groove
        groove_height = plate_height  # Z dimension (full height)
    
        # Groove starts 0.685714 from the left edge (left edge is at X = -plate_length/2 = -0.75)
        groove_start_x = -plate_length / 2 + 0.685714   # = -0.75 + 0.685714 = -0.064286
        groove_center_x = groove_start_x + groove_length / 2  # = -0.064286 + 0.042857 = -0.021429
    
        # --- Step 1: Create the base rectangular plate ---
        # Centered at origin in X and Y, starts at Z=0
        result = (
            cq.Workplane("XY")
            .box(plate_length, plate_width, plate_height,
                 centered=(True, True, False))
        )
    
        # --- Step 2: Create the slotted groove ---
        # The groove is on the front profile (XZ plane face), cuts through full Y depth
        result = (
            result
            .faces("<Y")          # front face (min Y)
            .workplane()          # workplane on front face
            .center(groove_center_x, plate_height / 2)  # center of groove in X, mid-height in Z
            .rect(groove_length, groove_height)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 1e-3
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - plate_length) < TOL, \
            f"X length: expected {plate_length}, got {bb.xlen}"
        assert abs(bb.ylen - plate_width) < TOL, \
            f"Y width: expected {plate_width}, got {bb.ylen}"
        assert abs(bb.zlen - plate_height) < TOL, \
            f"Z height: expected {plate_height}, got {bb.zlen}"
    
        # Bounding box position (centered in X and Y, starts at Z=0)
        assert abs(bb.xmin - (-plate_length / 2)) < TOL, \
            f"X min: expected {-plate_length/2}, got {bb.xmin}"
        assert abs(bb.xmax - (plate_length / 2)) < TOL, \
            f"X max: expected {plate_length/2}, got {bb.xmax}"
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - plate_height) < TOL, \
            f"Z max: expected {plate_height}, got {bb.zmax}"
    
        # Volume check: plate volume minus groove volume
        plate_vol  = plate_length * plate_width * plate_height
        groove_vol = groove_length * plate_width * groove_height
        expected_vol = plate_vol - groove_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Groove existence: probe a point inside the groove — should be outside the solid
        groove_probe = (groove_center_x, 0.0, plate_height / 2)
        assert not result.val().isInside(groove_probe), \
            f"Point inside groove should be outside the solid: {groove_probe}"
    
        # Check a point solidly inside the plate (away from groove) is inside
        solid_probe = (-0.6, 0.0, plate_height / 2)
        assert result.val().isInside(solid_probe), \
            f"Point inside plate should be inside the solid: {solid_probe}"
    
        # No cylindrical faces (groove is rectangular, no holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Face count analysis:
        # Original box: 6 faces (top, bottom, front, back, left, right)
        # Groove cuts through full Y depth and full Z height:
        #   - Top face split into 2 (left and right of groove)    → +1
        #   - Bottom face split into 2                            → +1
        #   - Front face split into 2 (left and right of opening) → +1
        #   - Back face split into 2                              → +1
        #   - Left and right side faces unchanged                 → 0
        #   - Two new groove side walls added (left and right)    → +2
        # Total: 6 + 1 + 1 + 1 + 1 + 2 = 12 faces
        face_count = result.faces().size()
        assert face_count == 12, f"Expected 12 faces, got {face_count}"
    
        print(f"All assertions passed!")
        print(f"  Plate: {plate_length} x {plate_width} x {plate_height}")
        print(f"  Groove center X: {groove_center_x:.6f}, width: {groove_length}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00996962/gpt_generated.stl')
