module top_module(
    input wire clk,      // 时钟信号
    input wire rst_n,    // 复位信号，低电平有效
    input wire start,    // 开始信号
    input wire stop,     // 停止信号
    input wire mode,     // 模式选择信号
    output wire [7:0] count, // 从计数器输出的计数值
    output wire done     // 从计数器输出的完成信号
);

    // 实例化 complex_fsm_counter 模块
    complex_fsm_counter uut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .stop(stop),
        .mode(mode),
        .count(count),
        .done(done)
    );

endmodule

module complex_fsm_counter(
    input wire clk,          // 时钟信号
    input wire rst_n,        // 复位信号，低电平有效
    input wire start,        // 开始计数
    input wire stop,         // 停止计数
    input wire mode,         // 模式选择，0：加法，1：减法
    output reg [7:0] count,  // 8位计数器
    output reg done          // 完成标志
);

    // 状态编码定义
    parameter IDLE       = 2'b00;
    parameter COUNT_UP   = 2'b01;
    parameter COUNT_DOWN = 2'b10;
    parameter DONE       = 2'b11;
    
    // 状态寄存器
    reg [1:0] current_state, next_state;
    
    // 时钟边沿触发的状态转移
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) 
            current_state <= IDLE; // 复位时进入空闲状态
        else 
            current_state <= next_state; // 状态转移
    end
    
    // 状态转移逻辑
    always @(*) begin
        case (current_state)
            IDLE: begin
                if (start) 
                    next_state = mode ? COUNT_DOWN : COUNT_UP; // 根据模式选择进入加法或减法状态
                else 
                    next_state = IDLE;
            end
            COUNT_UP: begin
                if (stop)
                    next_state = DONE; // 如果收到停止信号，进入完成状态
                else if (count == 8'hFF) 
                    next_state = DONE; // 如果计数器满了，也进入完成状态
                else 
                    next_state = COUNT_UP; // 继续加法计数
            end
            COUNT_DOWN: begin
                if (stop)
                    next_state = DONE; // 收到停止信号，进入完成状态
                else if (count == 8'h00) 
                    next_state = DONE; // 如果计数器为0，进入完成状态
                else 
                    next_state = COUNT_DOWN; // 继续减法计数
            end
            DONE: begin
                if (start) 
                    next_state = IDLE; // 完成后按下开始重新进入空闲状态
                else 
                    next_state = DONE;
            end
            default: next_state = IDLE;
        endcase
    end

    // 输出逻辑
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 8'h00;
            done <= 1'b0;
        end else begin
            case (current_state)
                IDLE: begin
                    count <= 8'h00; // 空闲状态时计数器清零
                    done <= 1'b0;
                end
                COUNT_UP: begin
                    count <= count + 1; // 计数器递增
                    done <= 1'b0;
                end
                COUNT_DOWN: begin
                    count <= count - 1; // 计数器递减
                    done <= 1'b0;
                end
                DONE: begin
                    done <= 1'b1; // 完成状态输出done信号
                end
            endcase
        end
    end

endmodule
