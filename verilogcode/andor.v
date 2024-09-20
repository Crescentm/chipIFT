module andor (
    input [3:0] x,
    input [3:0] y,
    input [3:0] z,
    output [3:0] o
);
assign o = x & (y | z);
endmodule
