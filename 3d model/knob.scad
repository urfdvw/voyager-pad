$fa = 1;
$fs = 0.4;

err = 0.1;
large_num = 200;

function mm(mil) = mil * 0.0254;
max_r = mm(850);
encoder_height = 7.5;
encoder_dent = 1.5;
encoder_r = 3;
encoder_rim_r = 0.6;
encoder_rim_h = encoder_height / 2;
knob_height = 10;
knob_r = 4;
knob_dent_r = 0.6;
knob_dent_offset = 0.2;
knob_dent_n = 16;
wheel_thickness = 3.5;
plate_r = 6;
frame_outer = 16;
frame_inner = 14.5;
rod_l = 20;
rod_r = 2;
rod_sink = 1;
rod_n = 8;
head_r = 2.5;

module encoder() {
    translate([0, 0, -err]) 
    cylinder(
        h = encoder_rim_h,
        r1 = encoder_r + encoder_rim_r,
        r2 = 0
    );
    difference() {
        translate([0, 0, -large_num + encoder_height]) 
            cylinder(h = large_num, r = encoder_r + err);
        translate([encoder_r - encoder_dent, -large_num / 2, -large_num / 2])
            cube(large_num);
    }
}

module knob(){
    translate([0, 0, knob_height])
    scale([1, 1, 0.4]) 
        sphere(r = knob_r);
    difference() {
        cylinder(h = knob_height, r = knob_r);
    }
}

module nice_knob() {
    difference() {
        knob();
        for ( i = [0 : knob_dent_n-1] ){
            rotate([0, 0, 360 / knob_dent_n * i]) 
            translate([knob_r + knob_dent_offset, 0, -large_num / 2]) 
            cylinder(h = large_num, r = knob_dent_r);
        }
    }
}

module wheel() {
    cylinder(h = wheel_thickness, r = plate_r);

    difference() {
        cylinder(h = wheel_thickness, r = frame_outer);
        translate([0, 0, -large_num / 2]) 
            cylinder(h = large_num, r = frame_inner);
    }

    difference(){
        for ( i = [0 : rod_n-1] ){
            translate([0, 0, rod_r - rod_sink]) 
                rotate([0, 0, 360 / rod_n * i])
                rotate([0, 90, 0]) 
                cylinder(r=rod_r, h=rod_l);
            rotate([0, 0, 360 / rod_n * i])
                translate([rod_l, 0, rod_r - rod_sink]) 
                sphere(r=head_r);
        }
        translate([-large_num / 2, -large_num / 2, -large_num]) 
        cube(large_num);
    }
}

difference() {
    union() {
        wheel();
        nice_knob();
    }
    encoder();
}