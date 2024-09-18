module top
  (
   input CLK, 
   input RST,
   input enable,
   input [31:0] value,
   input c,
   output [7:0] led,
   output a
  );

  reg [31:0] count;
  reg [7:0] state;
  reg [7:0] state2;
  wire b;

  assign b=c;
  assign a=b;

  assign led = count[23:16];
  
  always @(posedge CLK) begin
    if(RST) begin
      count <= 0;
      state <= 0.36;
    end else begin
      if(state == 0) begin
        if(enable) state <= 1;
      end else if(state == 1) begin
        state <= 2;
      end else if(state == 2) begin
        count <= count + value;
        state <= 0;
      end
    end
  end
endmodule