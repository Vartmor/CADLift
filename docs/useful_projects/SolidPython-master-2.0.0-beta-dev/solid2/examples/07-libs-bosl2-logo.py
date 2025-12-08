# include <BOSL2/std.scad>
# include <BOSL2/gears.scad>
# include <BOSL2/beziers.scad>
# include <BOSL2/screws.scad>
# include <BOSL2/cubetruss.scad>

from solid2.extensions.bosl2 import cuboid, regular_ngon, \
                                    RIGHT, FRONT, BACK, BOT, CENTER, \
                                    path_sweep, xdistribute

from solid2.extensions.bosl2 import gears, beziers, screws, cubetruss

# $fa=1;
# $fs=1;

from solid2 import set_global_fa, set_global_fs
set_global_fa(1)
set_global_fs(1)

def B():
	# recolor("#f77")
	# diff("hole")
	# cuboid([45,45,10], chamfer=10, edges=[RIGHT+BACK,RIGHT+FRONT], anchor=FRONT) {
	# 	cuboid([30,30,11], chamfer=5, edges=[RIGHT+BACK,RIGHT+FRONT], $tags="hole");
	# 	attach(FRONT,BACK, overlap=5) {
	# 		diff("hole")
	# 		cuboid([45,45,10], rounding=15, edges=[RIGHT+BACK,RIGHT+FRONT]) {
	# 			cuboid([30,30,11], rounding=10, edges=[RIGHT+BACK,RIGHT+FRONT], $tags="hole");
	# 		}
	# 	}
	# }

    upperHalf = cuboid([45,45,10], chamfer=10, edges=[RIGHT+BACK,RIGHT+FRONT],
                       anchor=FRONT)
    lowerHalf = cuboid([45,45,10], rounding=15, edges=[RIGHT+BACK,RIGHT+FRONT])

    upperHole = cuboid([30,30,11], chamfer=5, edges=[RIGHT+BACK,RIGHT+FRONT])
    lowerHole = cuboid([30,30,11], rounding=10, edges=[RIGHT+BACK,RIGHT+FRONT])

    upperHalf.add(upperHole.tag("hole"))
    lowerHalf.add(lowerHole.tag("hole"))

    upperHalf.add(lowerHalf.attach(FRONT, BACK, overlap=5))

    return upperHalf.diff("hole").recolor("#f77")

def O():
    # recolor("#7f7")
	# bevel_gear(pitch=8, teeth=20, face_width=12, shaft_diam=25, pitch_angle=45,
    #            slices=12, spiral_angle=30);
    gear = gears.bevel_gear(pitch=8, teeth=20, face_width=12, shaft_diam=25,
                            pitch_angle=45, slices=12, spiral_angle=30)

    return gear.recolor("#7f7")

def S():
	# x = 18;
	# y = 20;
	# s1 = 25;
	# s2 = 20;
	# sbez = [
	# 	            [-x,-y], [-x,-y-s1],
	# 	[ x,-y-s1], [ x,-y], [ x,-y+s2],
	# 	[-x, y-s2], [-x, y], [-x, y+s1],
	# 	[ x, y+s1], [ x, y]
	# ];
	# recolor("#99f")
	# path_sweep(regular_ngon(n=3,d=10,spin=90), bezpath_curve(sbez));

    x, y, s1, s2 = 18, 20, 25, 20
    sbez = [
                    [-x,-y], [-x,-y-s1],
        [ x,-y-s1], [ x,-y], [ x,-y+s2],
        [-x, y-s2], [-x, y], [-x, y+s1],
        [ x, y+s1], [ x, y]
    ]

    s = path_sweep(regular_ngon(n=3,d=10,spin=90), beziers.bezpath_curve(sbez))
    return s.recolor("#99f")

def L():
	# recolor("#0bf")
	# translate([-15,-35,0])
	# cubetruss_corner(size=10, strut=1, h=1, bracing=false, extents=[3,8,0,0,0],
    #                  clipthick=0);
    truss = cubetruss.cubetruss_corner(size=10, strut=1, h=1, bracing=False,
                                       extents=[3,8,0,0,0], clipthick=0)

    return truss.move([-15, -35, 0]).recolor("#0bf")

def II():
	# recolor("#777")
	# xdistribute(24) {
	# 	screw("M12,70", head="hex", anchor="origin", orient=BACK)
	# 		attach(BOT,CENTER)
	# 			nut("M12", thickness=10, diameter=20);
	# 	screw("M12,70", head="hex", anchor="origin", orient=BACK)
	# 		attach(BOT,CENTER)
	# 			nut("M12", thickness=10, diameter=20);
	# }

    screw = screws.screw("M12,70", head="hex", anchor="origin", orient=BACK)
    nut = screws.nut("M12", thickness=10)

    screw.add(nut.attach(BOT, CENTER))

    return xdistribute(24)(screw, screw).recolor("#777")

# xdistribute(50) { [...] }
xdistribute(50)(B(), O(), S(), L(), II()).save_as_scad()

