module mux2to1 (
    input wire a,    // 输入信号 a
    input wire b,    // 输入信号 b
    input wire sel,  // 选择信号 sel
    output wire y    // 输出 y
);
    assign y = (sel) ? b : a;
endmodule
module adder4bit (
    input wire [3:0] a,   // 4 位输入 a
    input wire [3:0] b,   // 4 位输入 b
    input wire cin,       // 输入进位 cin
    output wire [3:0] sum, // 4 位和 sum
    output wire cout      // 输出进位 cout
);
    wire [4:0] result;    // 用于存储加法结果的中间变量

    assign result = a + b + cin;
    assign sum = result[3:0];
    assign cout = result[4];

endmodule
