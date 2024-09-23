module logical (
    input [1: 0] x,
    input [1: 0] y,
    output land,
    output lor,
    output lnot
);
assign land = x && y;
assign lor = x || y;
assign lnot = !x;
endmodule