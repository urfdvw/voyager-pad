$fa = 1;
$fs = 0.4;

function mm(mil) = mil * 0.0254;
board_r = mm(800);
board_l = mm(4100);
board_thickness = 1.6;
print_err = 0.5;
plate_raise = 5;
large_num = 200;

frame_height = plate_raise - board_thickness;
frame_thick = 1.5;
frame_r = board_r - print_err;
frame_l = board_l - print_err;

module frame_outter() {
    cylinder(
        h = frame_height, 
        r = frame_r
    );
    translate([0, -frame_r, 0])
        cube([frame_l, frame_r*2, frame_height]);
}

module frame_inner() {
    translate([0, 0, - 0.5 * large_num])
        cylinder(
            h = large_num, 
            r = frame_r - frame_thick
        );
    translate([0, -(frame_r - frame_thick), - 0.5 * large_num])
        cube([frame_l - frame_thick, (frame_r - frame_thick)*2, large_num]);
}

// main
difference () {
    frame_outter();
    frame_inner();
}