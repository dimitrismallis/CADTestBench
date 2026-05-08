import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    from cadquery import selectors
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        block_length = 0.448905   # X dimension
        block_width  = 0.75       # Y dimension
        block_height = 0.136861   # Z (extrusion depth)
    
        hole_length = 0.328467    # X dimension of each hole
        hole_width  = 0.229927    # Y dimension of each hole
        hole_gap    = 0.104015    # gap between the two holes (along Y)
        fillet_r    = 0.02        # rounded corner radius for holes
    
        # --- Step 1: Create the base block ---
        block = cq.Workplane("XY").rect(block_length, block_width).extrude(block_height)
    
        # --- Step 2: Compute hole center positions ---
        # Holes arranged along Y axis, symmetric about Y=0
        hole_center_y = hole_gap / 2 + hole_width / 2  # = 0.052008 + 0.114964 = 0.166971
    
        # --- Step 3: Create hole cutters as separate solids and subtract ---
        hole1 = (
            cq.Workplane(cq.Plane(origin=(0, hole_center_y, block_height),
                                   xDir=(1, 0, 0), normal=(0, 0, 1)))
            .rect(hole_length, hole_width)
            .extrude(block_height)
        )
    
        hole2 = (
            cq.Workplane(cq.Plane(origin=(0, -hole_center_y, block_height),
                                   xDir=(1, 0, 0), normal=(0, 0, 1)))
            .rect(hole_length, hole_width)
            .extrude(block_height)
        )
    
        # Cut holes from block
        result = block.cut(hole1).cut(hole2)
    
        # --- Step 4: Fillet the vertical edges of the holes ---
        # Use OCC TopExp_Explorer to get edges directly from the solid topology
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopAbs import TopAbs_EDGE, TopAbs_SOLID, TopAbs_COMPOUND
        from OCP.BRepAdaptor import BRepAdaptor_Curve
        from OCP.GeomAbs import GeomAbs_Line
        from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
        from OCP.TopoDS import TopoDS_Iterator, TopoDS_Edge
        from cadquery import Solid, Compound
    
        bx = block_length / 2
        by = block_width / 2
        tol = 0.001
    
        solid_occ = result.val().wrapped
    
        # Explore all edges in the solid directly from OCC topology
        explorer = TopExp_Explorer(solid_occ, TopAbs_EDGE)
        inner_edges_occ = []
        seen_positions = set()
    
        while explorer.More():
            # Get current edge as TopoDS_Edge
            current_shape = explorer.Current()
            edge_occ = TopoDS_Edge(current_shape)
            explorer.Next()
    
            # Check geometry type - must be a straight line
            adaptor = BRepAdaptor_Curve(edge_occ)
            if adaptor.GetType() != GeomAbs_Line:
                continue
    
            # Get start and end points
            p1 = adaptor.Value(adaptor.FirstParameter())
            p2 = adaptor.Value(adaptor.LastParameter())
    
            dx = abs(p2.X() - p1.X())
            dy = abs(p2.Y() - p1.Y())
            dz = abs(p2.Z() - p1.Z())
    
            # Must be vertical (parallel to Z): no X or Y change, has Z change
            if dz < tol:
                continue
            if dx > tol or dy > tol:
                continue
    
            # Center of edge
            cx = (p1.X() + p2.X()) / 2
            cy = (p1.Y() + p2.Y()) / 2
    
            # Not on outer boundary of block
            on_outer = (
                abs(abs(cx) - bx) < tol or
                abs(abs(cy) - by) < tol
            )
            if on_outer:
                continue
    
            # Deduplicate by XY position
            pos_key = (round(cx, 4), round(cy, 4))
            if pos_key in seen_positions:
                continue
            seen_positions.add(pos_key)
            inner_edges_occ.append(edge_occ)
    
        print(f"Inner vertical edges found: {len(inner_edges_occ)}")
    
        # Apply fillet using OCC BRepFilletAPI_MakeFillet
        fillet_maker = BRepFilletAPI_MakeFillet(solid_occ)
        for e_occ in inner_edges_occ:
            fillet_maker.Add(fillet_r, e_occ)
        fillet_maker.Build()
        print(f"Fillet IsDone: {fillet_maker.IsDone()}")
    
        occ_shape = fillet_maker.Shape()
        shape_type = occ_shape.ShapeType()
    
        if shape_type == TopAbs_SOLID:
            filleted_solid = Solid(occ_shape)
        elif shape_type == TopAbs_COMPOUND:
            it = TopoDS_Iterator(occ_shape)
            solids = []
            while it.More():
                s = it.Value()
                if s.ShapeType() == TopAbs_SOLID:
                    solids.append(Solid(s))
                it.Next()
            if len(solids) == 1:
                filleted_solid = solids[0]
            else:
                filleted_solid = Compound.makeCompound(solids)
        else:
            from cadquery import Shape
            filleted_solid = Shape.cast(occ_shape)
    
        result = cq.Workplane("XY").newObject([filleted_solid])
    
        # --- Final object verification ---
        TOL = 0.01
    
        final_bb = result.val().BoundingBox()
    
        # Check overall bounding box
        assert abs(final_bb.xlen - block_length) < TOL, \
            f"X length: expected {block_length}, got {final_bb.xlen}"
        assert abs(final_bb.ylen - block_width) < TOL, \
            f"Y width: expected {block_width}, got {final_bb.ylen}"
        assert abs(final_bb.zlen - block_height) < TOL, \
            f"Z height: expected {block_height}, got {final_bb.zlen}"
    
        # Volume check:
        # block - 2 rectangular holes - fillet material removed at 8 inner corners
        # Each concave corner fillet removes: r^2*(1 - pi/4)*h
        block_vol = block_length * block_width * block_height
        hole_vol_each = hole_length * hole_width * block_height
        corner_removed = fillet_r**2 * (1.0 - math.pi / 4.0) * block_height
        expected_vol = block_vol - 2.0 * hole_vol_each - 8.0 * corner_removed
        actual_vol = result.val().Volume()
        # Use absolute tolerance of 0.0005
        assert abs(actual_vol - expected_vol) < 0.0005, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces: 8 rounded corners (4 per hole × 2 holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 8, \
            f"Cylindrical faces (rounded corners): expected 8, got {cyl_faces}"
    
        # Check symmetry: center of mass at x=0, y=0, z=block_height/2
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - block_height / 2) < TOL, \
            f"Center of mass Z: expected {block_height/2}, got {com.z}"
    
        # Check holes exist: points at hole centers should be outside the solid
        solid = result.val()
        hole1_center = (0, hole_center_y, block_height / 2)
        assert not solid.isInside(hole1_center), \
            f"Point {hole1_center} should be outside solid (inside hole 1)"
        hole2_center = (0, -hole_center_y, block_height / 2)
        assert not solid.isInside(hole2_center), \
            f"Point {hole2_center} should be outside solid (inside hole 2)"
        # Point between holes should be inside solid
        mid_point = (0, 0, block_height / 2)
        assert solid.isInside(mid_point), \
            f"Point {mid_point} should be inside solid (between holes)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997878/gpt_generated.stl')
