// Auto-generated lib.v


module nnd2s1 (
    input DIN1,
    input DIN2,
    output Q
);
    assign Q = ~(DIN1 & DIN2);
endmodule

module or5s1 (
    input DIN1,
    input DIN2,
    input DIN3,
    input DIN4,
    input DIN5,
    output Q
);
    assign Q = DIN1 | DIN2 | DIN3 | DIN4 | DIN5;
endmodule

module xor2s1 (
    input DIN1,
    input DIN2,
    output Q
);
    assign Q = DIN1 ^ DIN2;
endmodule

module hi1s1 (
    input DIN,  // 数据输入
    output Q    // 输出
);
    assign Q = DIN;  // 将输入信号传递到输出
endmodule

module nor2s1 (
    input DIN1,
    input DIN2,
    output Q
);
    assign Q = ~(DIN1 | DIN2);
endmodule

module nnd4s1 (
    input DIN1,
    input DIN2,
    input DIN3,
    input DIN4,
    output Q
);
    assign Q = ~(DIN1 & DIN2 & DIN3 & DIN4);
endmodule
