module multiplier (
    input wire a,
    input wire b,
    output wire product
);
    assign product = a & b; // 简单的位乘法（按位与）
endmodule
module adder (
    input wire a,
    input wire b,
    output wire sum
);
    wire product; // 中间信号用于连接 multiplier 的输出

    // 实例化 multiplier 模块
    multiplier mult_inst (
        .a(a),
        .b(b),
        .product(product)
    );

    // 加法器的输出依赖于 multiplier 的输出
    assign sum = a ^ b ^ product; // 简单的位加法，包含 multiplier 的结果
endmodule
module top (
    input wire a1, b1,
    input wire a2, b2,
    output wire sum1,
    output wire sum2
);
    // 实例化第一个 adder 模块
    adder adder_inst1 (
        .a(a1),
        .b(b1),
        .sum(sum1)
    );

    // 实例化第二个 adder 模块
    adder adder_inst2 (
        .a(a2),
        .b(b2),
        .sum(sum2)
    );
endmodule
