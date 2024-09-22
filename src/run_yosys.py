import json
import subprocess
import sys
import os
import shutil

def parse_config(config_json_file):
    with open(config_json_file, "r") as f:
        config = json.load(f)
    top_module = config["top_module"]
    conditions = config["conditions"]
    return top_module, conditions

def run_yosys_sat(run_ys_file, verilog_file, result_json_file, top_module, condition):
    ys_script = []

    ys_script.append(f"read_verilog {verilog_file}")

    ys_script.append(f"hierarchy -top {top_module}")

    ys_script.append("proc; opt; flatten")

    sat_cmd = "sat"

    sat_options = condition.get("sat_options", {})

    if "set" in sat_options:
        for signal, value in sat_options["set"].items():
            value_int = int(value, 2)  # 二进制字符串
            sat_cmd += f" -set {signal}_t {value_int}"

    if "show" in sat_options:
        for signal in sat_options["show"]:
            sat_cmd += f" -show {signal}_t"

    sat_cmd += f" -dump_json {result_json_file}"


    ys_script.append(sat_cmd)

    with open(run_ys_file, "w") as f:
        f.write("\n".join(ys_script))

    try:
        result = subprocess.run(
            ["yosys", run_ys_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print("Yosys 执行错误：", e.stderr)
        sys.exit(1)

    if os.path.exists(result_json_file):
        with open(result_json_file, "r") as f:
            result_json = json.load(f)

        actual_signals = {}
        for signal in result_json["signal"]:
            name = signal["name"]
            if "data" in signal and signal["data"]:
                value = signal["data"][0]
                actual_signals[name] = value
            else:
                actual_signals[name] = None


        # 比较输出信号
        output_differences = {}
        for signal, expected_value in condition.get("expected_output_signals", {}).items():
            signal=signal+"_t"
            actual_value = actual_signals.get(signal)
            if actual_value is not None:
                differences = compare_bits(actual_value, expected_value)
                if differences:
                    output_differences[signal] = differences

        # 输出差异报告
        if output_differences:
            print(f"Condition '{condition.get('name', 'Unnamed')}' Failed:")
            for signal, diffs in output_differences.items():
                print(f"Output Signal {signal}:")
                for diff in diffs:
                    print(f"  {diff}")
        else:
            print(f"Condition '{condition.get('name', 'Unnamed')}' Passed.")
    else:
        print(f"Result JSON file '{result_json_file}' not found.")

def copy_result_json(result_json_file, output_dir, condition):
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"无法创建输出目录 '{output_dir}'：{e}")
            sys.exit(1)
    
    new_filename = f"{condition.get('name', 'Unnamed')}.json"
    destination = os.path.join(output_dir, new_filename)
    shutil.copyfile(result_json_file, destination)

def compare_bits(actual_value, expected_value):
    differences = []
    max_len = max(len(actual_value), len(expected_value))
    actual_value = actual_value.zfill(max_len)
    expected_value = expected_value.zfill(max_len)

    for i in range(max_len):
        bit_pos = max_len - i  
        actual_bit = actual_value[i]
        expected_bit = expected_value[i]
        if actual_bit != expected_bit:
            differences.append(f"Bit {bit_pos}: Actual {actual_bit}, Expected {expected_bit}")
    return differences



if __name__ == "__main__":
    run_ys_file = "run.ys"
    config_json_file = "config.json"
    verilog_file = "And_t.v"
    result_json_file_temp = "result_temp.json"
    result_folder="Result"

    top_module, conditions = parse_config(config_json_file)

    for condition in conditions:
        run_yosys_sat(run_ys_file, verilog_file, result_json_file_temp, top_module, condition)
        copy_result_json(result_json_file_temp, result_folder, condition)
    
