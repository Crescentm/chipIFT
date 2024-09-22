module top (
    input  x,
    input  y,
    input  z,
    output o
);
assign o = x & (y | z);
endmodule
