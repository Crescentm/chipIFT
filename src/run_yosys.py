import json
import subprocess
import sys
import os

def yosys_sat():
    # 读取配置文件
    with open('config.json', 'r') as f:
        config = json.load(f)
    ys_script = []
    ys_script.append(f"read_verilog {config['verilog_file']}")
    ys_script.append(f"hierarchy -top {config['top_module']}")
    ys_script.append("proc; opt; flatten")
    sat_cmd = "sat"
    if 'set' in config['sat_options']:
        for signal, value in config['sat_options']['set'].items():
            sat_cmd += f" -set {signal} {value}"

    if 'show' in config['sat_options']:
        for signal in config['sat_options']['show']:
            sat_cmd += f" -show {signal}"

    if 'dump_json' in config['sat_options']:
        dump_json_file = config['sat_options']['dump_json']
        sat_cmd += f" -dump_json {dump_json_file}"
    else:
        dump_json_file = None

    # 将 sat 命令添加到脚本
    ys_script.append(sat_cmd)

    # 将脚本内容写入文件
    with open('run.ys', 'w') as f:
        f.write('\n'.join(ys_script))

    # 运行 Yosys 并捕获输出
    try:
        result = subprocess.run(['yosys', 'run.ys'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Yosys 执行错误：", e.stderr)
        sys.exit(1)

    # 打印 Yosys 输出结果
    print(result.stdout)

    # 检查是否生成了 dump_json 文件
    if dump_json_file and os.path.exists(dump_json_file):
        # 读取结果 JSON 文件
        with open(dump_json_file, 'r') as f:
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

        if output_differences:
            print("difference：")
            for signal, diffs in output_differences.items():
                print(f"signal {signal}:")
                for diff in diffs:
                    print(f"  {diff}")
        else:
            print("Q.E.D.")
    else:
        print("json no found")

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
    yosys_sat()

