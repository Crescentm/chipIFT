module bitwiseand (
    input [3:0] x,
    input [3:0] y,
    output [3:0] o
);
assign o = x & y;
endmodule
