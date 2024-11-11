module condition_if(
    input cond1,
    input cond2,
    input v1,
    input v2,
    output o
);
always@(*) begin
    if (cond1) begin
        o = v1;
    end else begin
        if(cond2) begin
            o = v2;
        end else begin
            o = v1;
        end
    end
end
endmodule
