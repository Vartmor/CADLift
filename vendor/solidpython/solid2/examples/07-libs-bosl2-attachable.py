from solid2.extensions.bosl2 import cube, sphere, xcyl, union, xcopies, \
                                    attachable, show_anchors, \
                                    CENTER, LEFT, TOP, UP

def cubic_barbell(s=100, anchor=CENTER, spin=0, orient=UP):
    return attachable(anchor,spin,orient, size=[s*3,s,s]) (
        union() (
            xcopies(2*s)(cube(s, center=True)),
            xcyl(h=2*s, d=s/4)
        )
    )

cc = cubic_barbell(100)(
        cube(50, center=True).attach(TOP),
        sphere(50).attach(LEFT),
        show_anchors(30)
    )

cc.save_as_scad()

