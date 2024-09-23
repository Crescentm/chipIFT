module  equality (
    input [1: 0] x,
    input [1: 0] y,
    output eq,
    output neq,
    output eql,
    output nel
);
assign eq = x == y;
assign neq = x != y;
assign eql = x === y;
assign nel = x !== y;
endmodule