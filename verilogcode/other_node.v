module top #(
    parameter WIDTH = 4
)(
    input [WIDTH - 1: 0] x,
    input [WIDTH - 1: 0] y,
    output [WIDTH - 1: 0] o1,
    output [WIDTH - 1: 0] o2
);
assign o1 = {WIDTH{1'b1}};
assign o2[0] = y[WIDTH - 1];
assign o2[WIDTH - 1: 1] = y[WIDTH - 2: 0];
endmodule
