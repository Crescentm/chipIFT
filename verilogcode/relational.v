module relational (
    input [1: 0] x,
    input [1: 0] y,
    output lt,
    output le,
    output gt,
    output ge
);
assign lt = x < y;
assign le = x <= y;
assign gt = x > y;
assign ge = x >= y;
endmodule