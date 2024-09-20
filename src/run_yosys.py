import json
import subprocess
import sys
import os

def run_yosys(run_ys_file, config_json_file, verilog_file, result_json_file):
    # 读取配置文件
    with open(config_json_file, 'r') as f:
        config = json.load(f)

    # 更新配置中的 Verilog 文件名
    config['verilog_file'] = verilog_file

    # 构建 Yosys 脚本内容
    ys_script = []

    # 读取 Verilog 文件
    ys_script.append(f"read_verilog {config['verilog_file']}")

    # 指定顶层模块
    ys_script.append(f"hierarchy -top {config['top_module']}")

    # 执行必要的优化
    ys_script.append("proc; opt; flatten")

    # 构建 sat 命令
    sat_cmd = "sat"

    # 添加 set 选项
    if 'set' in config['sat_options']:
        for signal, value in config['sat_options']['set'].items():
            sat_cmd += f" -set {signal} {value}"

    # 添加 show 选项
    if 'show' in config['sat_options']:
        for signal in config['sat_options']['show']:
            sat_cmd += f" -show {signal}"

    # 添加 dump_json 选项，使用 result_json_file
    if 'dump_json' in config['sat_options']:
        sat_cmd += f" -dump_json {result_json_file}"

    # 将 sat 命令添加到脚本
    ys_script.append(sat_cmd)

    # 将脚本内容写入文件
    with open(run_ys_file, 'w') as f:
        f.write('\n'.join(ys_script))

    # 运行 Yosys 并捕获输出
    try:
        result = subprocess.run(['yosys', run_ys_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Yosys 执行错误：", e.stderr)
        sys.exit(1)

    # 打印 Yosys 输出结果
    print(result.stdout)

    # 检查是否生成了 result_json_file
    if os.path.exists(result_json_file):
        # 读取结果 JSON 文件
        with open(result_json_file, 'r') as f:
            result_json = json.load(f)

        # 提取实际信号值
        actual_signals = {}
        for signal in result_json['signal']:
            name = signal['name']
            if 'data' in signal and signal['data']:
                # 获取信号的值，取第一个时间点的值
                value = signal['data'][0]
                actual_signals[name] = value
            else:
                actual_signals[name] = None

        # 比较输入信号的实际值和设定值
        input_differences = {}
        for signal, expected_value in config.get('input_signals', {}).items():
            actual_value = actual_signals.get(signal)
            if actual_value is not None:
                expected_value_bin = format(expected_value, f'0{len(actual_value)}b')
                differences = compare_bits(actual_value, expected_value_bin)
                if differences:
                    input_differences[signal] = differences

        # 比较输出信号的实际值和期望值
        output_differences = {}
        for signal, expected_value in config.get('expected_output_signals', {}).items():
            actual_value = actual_signals.get(signal)
            if actual_value is not None:
                expected_value_bin = format(expected_value, f'0{len(actual_value)}b')
                differences = compare_bits(actual_value, expected_value_bin)
                if differences:
                    output_differences[signal] = differences

        # 输出差异报告
        if input_differences:
            print("输入信号存在以下位级别差异：")
            for signal, diffs in input_differences.items():
                print(f"信号 {signal}:")
                for diff in diffs:
                    print(f"  {diff}")
        else:
            print("输入信号与设定值一致。")

        if output_differences:
            print("输出信号存在以下位级别差异：")
            for signal, diffs in output_differences.items():
                print(f"信号 {signal}:")
                for diff in diffs:
                    print(f"  {diff}")
        else:
            print("输出信号与期望值一致。")
    else:
        print(f"未找到结果 JSON 文件 {result_json_file}，无法比较信号差异。")

def compare_bits(actual_value, expected_value):
    differences = []
    # 确保两者长度一致
    max_len = max(len(actual_value), len(expected_value))
    actual_value = actual_value.zfill(max_len)
    expected_value = expected_value.zfill(max_len)

    # 比较每个位
    for i in range(max_len):
        bit_pos = max_len - i  # 位位置，从高位到低位
        actual_bit = actual_value[i]
        expected_bit = expected_value[i]
        if actual_bit != expected_bit:
            differences.append(f"位 {bit_pos}: 实际值 {actual_bit}, 期望值 {expected_bit}")
    return differences

if __name__ == "__main__":
    # 示例调用
    run_yosys('run.ys', 'config.json', 'And_t.v', 'result.json')

