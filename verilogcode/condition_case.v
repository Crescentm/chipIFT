module condition_case (
    input cond,
    input value0,
    input value1,
    output result
);
always @(*) begin
    case(cond)
        1'b0: begin
            result = value0;
        end
        1'b1: begin
            result = value1;
        end
        default: result = 0;
    endcase
end
endmodule
