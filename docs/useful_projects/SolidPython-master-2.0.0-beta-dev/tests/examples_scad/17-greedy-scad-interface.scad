$fn = 32;
$vpd = ((abs(sin(($t * 360))) * 10) + 5);
$vpt = [0, -1, 0];
$vpr = [63, 0, ($t * 360)];
$vpf = 25;
/* [Colors] */
//The color of the cube
cube_color = "blue"; //[red, green, blue]
/* [Animation] */
//Animation speed factor
anim_factor = 1; //[1:0.5:10]

union() {
	color(alpha = 1.0, c = cube_color) {
		cube(center = true, size = abs(sin((($t * 360) * anim_factor))));
	}
	translate(v = [0, -2, 0]) {
		color(alpha = 1.0, c = cube_color) {
			sphere(r = abs(sin(((($t * 360) * anim_factor) - 90))));
		}
	}
}
