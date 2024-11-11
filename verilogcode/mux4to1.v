module mux4to1 (
    input wire [1:0] sel,  // 2-bit select signal
    input wire [3:0] in0,  // Input 0
    input wire [3:0] in1,  // Input 1
    input wire [3:0] in2,  // Input 2
    input wire [3:0] in3,  // Input 3
    output reg [3:0] out   // Output
);

    always @(*) begin
        // 使用 if 语句
        if (sel == 2'b00)
            out = in0;
        if (sel == 2'b01) begin
            out = in1;
        end else if (sel == 2'b10) begin
            out = in2;
        end else if (sel == 2'b11) begin
            out = in3;
        end else if (sel!=2'b11 && sel!= 2'b10 && sel!=2'b01) begin
            out = in1;
        end else begin
            out = 4'b0000; // 默认输出
        end

        // 使用 case 语句
        case (sel)
            2'b00: out = in0;
            2'b01: out = in1;
            2'b10: out = in2;
            2'b11: out = in3;
            default: out = 4'b0000; // 默认输出
        endcase
    end
endmodule
