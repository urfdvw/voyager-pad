$fa = 1;
$fs = 0.4;

function mm(mil) = mil * 0.0254;
board_r = mm(800);
board_l = mm(4100);
board_thickness = 1.6;
cap_raise = 11;
port_center_x = mm(1400 - 700);
port_height = 8;
port_width = 13;
support_width = 5;
support_l = 70;
case_thickness = 2;

print_err = 0.1;
err = 0.01;
large_num = 200;

module case_outter() {
    outer_height = case_thickness 
                + port_height 
                + board_thickness
                + cap_raise;
    outer_r = board_r + case_thickness;
    outer_l = board_l + case_thickness;
    cylinder(
        h = outer_height, 
        r = outer_r
    );
    translate([0, -outer_r, 0])
        cube([outer_l, outer_r*2, outer_height]);
}

module case_inner() {
    inner_height = port_height 
                 + board_thickness
                 + cap_raise
                 + err;
    translate([0, 0, case_thickness])
        cylinder(
            h = inner_height, 
            r = board_r + print_err
        );
    translate([0, -(board_r + print_err), case_thickness])
        cube([board_l, (board_r + print_err) * 2, inner_height]);
    
}

module port() {
    translate([
        - 0.5 * port_width + port_center_x,
        0,
        case_thickness
    ])
        cube([port_width, large_num, port_height]);
}

module port_bottom() {
    translate([port_center_x, 0, 0])
        cube([13, 10, large_num], center=true);
}

module round_support() {
    difference() {
        cylinder(
            h = port_height + board_thickness, 
            r = board_r + err + print_err
        );
        translate([0, 0, -large_num / 2])
            cylinder(
                h = large_num, 
                r = board_r - support_width
            );
        translate([0, -large_num / 2, 0])
            cube(large_num);
    }
}

module bar_support() {
    difference() {
        translate([board_l - support_l + err, -(board_r + err + print_err) ,0])
            cube([support_l, (board_r + err + print_err) * 2, port_height + board_thickness]);
        translate([0, -(board_r - support_width), 0])
            cube([large_num, (board_r - support_width) * 2, large_num]);
    }
}

// main
difference(){
    union() {
        difference() {
            case_outter();
            case_inner();
        }
        round_support();
        bar_support();
    }
    port();
    port_bottom();
}
