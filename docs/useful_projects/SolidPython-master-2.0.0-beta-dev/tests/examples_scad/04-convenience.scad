difference() {
	rotate(a = [45, 45, 45]) {
		translate(v = [0, 0, -5]) {
			cube(size = [10, 20, 30]);
		}
	}
	#translate(v = [0, 5, 0]) {
		sphere(r = 10);
	}
}
