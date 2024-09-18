module mux2to1 (
    input wire a,     // 输入信号 a
    input wire b,     // 输入信号 b
    input wire sel,   // 选择信号 sel
    output wire y     // 输出 y
);
    // 根据选择信号 sel 选择 a 或 b 作为输出
    assign y = sel ? b : a;
endmodule
module full_adder (
    input wire a,     // 输入信号 a
    input wire b,     // 输入信号 b
    input wire cin,   // 进位输入 cin
    output wire sum,  // 和输出 sum
    output wire cout  // 进位输出 cout
);
    // 全加器的逻辑
    assign sum = a ^ b ^ cin;     // 异或逻辑得到和
    assign cout = (a & b) | (cin & (a ^ b));  // 进位输出
endmodule
module top_module;
    // 信号定义
    reg a, b, sel;          // 选择器的输入信号
    wire mux_out;           // 选择器的输出

    reg a_fa, b_fa, cin_fa; // 全加器的输入信号
    wire sum_fa, cout_fa;   // 全加器的输出信号

    // 实例化 2:1 选择器
    mux2to1 u_mux (
        .a(a),        // 输入 a 连接到 reg a
        .b(b),        // 输入 b 连接到 reg b
        .sel(sel),    // 选择信号 sel
        .y(mux_out)   // 输出连接到 wire mux_out
    );

    // 实例化全加器
    full_adder u_full_adder (
        .a(a_fa),     // 输入 a 连接到 reg a_fa
        .b(b_fa),     // 输入 b 连接到 reg b_fa
        .cin(cin_fa), // 进位输入 cin_fa
        .sum(sum_fa), // 和输出连接到 wire sum_fa
        .cout(cout_fa) // 进位输出连接到 wire cout_fa
    );

    // 测试信号初始化
    initial begin
        // 测试 2:1 选择器
        a = 1'b0; b = 1'b1; sel = 1'b0;
        #10 sel = 1'b1;

        // 测试全加器
        a_fa = 1'b0; b_fa = 1'b1; cin_fa = 1'b0;
        #10 cin_fa = 1'b1;
        #10 a_fa = 1'b1; b_fa = 1'b1; cin_fa = 1'b1;

    end
endmodule


