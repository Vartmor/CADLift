union() {
	cube(center = true, size = [100, 250, 50]);
	translate(v = [0, 0, 50]) {
		difference() {
			cube(center = true, size = [80, 100, 60]);
			union() {
				translate(v = [0, 0, -10]) {
					cube(center = true, size = [200, 55, 50]);
				}
				rotate(a = [0, 0, 90]) {
					translate(v = [0, 0, -10]) {
						cube(center = true, size = [200, 55, 50]);
					}
				}
			}
		}
	}
	translate(v = [0, -80, 0]) {
		translate(v = [0, 0, -20]) {
			union() {
				translate(v = [-70, 0, 0]) {
					rotate(a = [0, 90, 0]) {
						cylinder(center = true, h = 15, r = 35);
					}
				}
				translate(v = [70, 0, 0]) {
					rotate(a = [0, 90, 0]) {
						cylinder(center = true, h = 15, r = 35);
					}
				}
				rotate(a = [0, 90, 0]) {
					cylinder(center = true, h = 120, r = 10);
				}
			}
		}
	}
	translate(v = [0, 80, 0]) {
		translate(v = [0, 0, -20]) {
			union() {
				translate(v = [-70, 0, 0]) {
					rotate(a = [0, 90, 0]) {
						cylinder(center = true, h = 15, r = 35);
					}
				}
				translate(v = [70, 0, 0]) {
					rotate(a = [0, 90, 0]) {
						cylinder(center = true, h = 15, r = 35);
					}
				}
				rotate(a = [0, 90, 0]) {
					cylinder(center = true, h = 120, r = 10);
				}
			}
		}
	}
}
