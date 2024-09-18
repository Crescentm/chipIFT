module adder_array #(parameter WIDTH = 4) (
    input [WIDTH-1:0] a,
    input [WIDTH-1:0] b,
    output [WIDTH-1:0] sum
);
    genvar i;
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin : adder_gen
            assign sum[i] = a[i] ^ b[i]; // 简单的位加法（不带进位）
        end
    endgenerate
endmodule
