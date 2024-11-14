import json
import subprocess
import sys
import os
import shutil
import re
from typing import List, Dict


def parse_output(output, is_sequential):
    lines = output.splitlines()
    table_start = False
    data = {}
    data_time = {}

    if is_sequential is True:
        for i, line in enumerate(lines):
            # 查找表头
            if re.match(r"\s*Time\s+Signal Name\s+Dec\s+Hex\s+Bin", line):
                table_start = True
                continue
            if table_start:
                if re.match(r"\s*-+", line):
                    continue
                if line.strip() == "" or "End of script" in line:
                    break
                parts = re.split(r"\s{1,}", line.strip())
                if len(parts) == 5:
                    time, signal_name, dec, hex_val, bin_val = parts
                    # 去除信号名称前的反斜杠
                    signal_name = signal_name.lstrip("\\")
                    data[signal_name] = {"Dec": dec, "Hex": hex_val, "Bin": bin_val}
                    data_time[time] = data
        return data_time
    else:
        for i, line in enumerate(lines):
            # 查找表头
            if re.match(r"\s*Signal Name\s+Dec\s+Hex\s+Bin", line):
                table_start = True
                continue
            if table_start:
                if re.match(r"\s*-+", line):
                    continue
                if line.strip() == "" or "Dumping SAT model" in line:
                    break
                parts = re.split(r"\s{2,}", line.strip())
                if len(parts) == 4:
                    signal_name, dec, hex_val, bin_val = parts
                    # 去除信号名称前的反斜杠
                    signal_name = signal_name.lstrip("\\")
                    data[signal_name] = {"Dec": dec, "Hex": hex_val, "Bin": bin_val}
        return data


def save_to_json(data, filename):
    """将数据保存为 JSON 文件"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[E] Unable to save json: {e}")


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

    ys_script.append(
        "proc;  flatten; memory -nomap ; fsm ; opt ; opt_expr ; opt_merge ; opt_reduce "
    )
    ys_script.append("opt_muxtree; opt_dff ; opt_clean ; opt_share   ")
    ys_script.append("dfflegalize -cell $_DFF_P_ 0 ")
    ys_script.append("simplemap")
    sat_cmd = "sat"

    sat_cmd += " -ignore_unknown_cells"

    # 检查是否为时序电路，并添加 -seq 选项
    is_sequential = condition.get("is_sequential", False)
    seq_steps = (
        int(condition.get("seq", None))
        if condition.get("seq", None) is not None
        else None
    )

    if is_sequential and seq_steps is not None:
        timing_signal = condition.get("timing_signal", None)
        if timing_signal is None:
            timing_signal = "clk"
        sat_cmd += f" -seq {seq_steps}"
        for step in range(1, seq_steps + 1):
            clk_value = step % 2  # 交替设置 clk 为 0 和 1
            sat_cmd += f" -set-at {step} {timing_signal} {clk_value}" # FIXME: clock signal should be user defined
        sat_cmd += f" -show {timing_signal}" # FIXME

    sat_options = condition.get("sat_options", {})

    if "set" in sat_options:
        for signal, value in sat_options["set"].items():
            value_int = int(value, 2)  # 二进制字符串
            sat_cmd += f" -set {signal}_t {value_int}"

    if "prove" in sat_options:
        for signal, value in sat_options["prove"].items():
            value_int = int(value, 2)  # 二进制字符串
            sat_cmd += f" -prove {signal}_t {value_int}"

    if "show" in sat_options:
        for signal in sat_options["show"]:
            sat_cmd += f" -show {signal}_t"

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
        print(f"[E]Yosys execution error: {e.stderr}")
        sys.exit(1)

    output = result.stdout
    data = parse_output(output, is_sequential)
    save_to_json(data, result_json_file)

    if os.path.exists(result_json_file):
        if is_sequential is False:
            with open(result_json_file, "r") as f:
                result_json = json.load(f)

            actual_signals = {}
            for signal, values in result_json.items():
                if isinstance(values, dict):
                    bin_value = values.get("Bin")
                    actual_signals[signal] = bin_value
                else:
                    actual_signals[signal] = None
            output_differences = {}
            for signal, expected_value_bin in condition.get(
                "expected_output_signals", {}
            ).items():
                signal += "_t"
                actual_value = actual_signals.get(signal)
                if actual_value is not None:
                    # Compare bits
                    differences = compare_bits(actual_value, expected_value_bin)
                    if differences:
                        output_differences[signal] = differences
                else:
                    output_differences[signal] = ["Signal not found in results"]

            # 输出差异报告
            if output_differences:
                print(f"Condition '{condition.get('name', 'Unnamed')}' Failed:")
                for signal, diffs in output_differences.items():
                    print(f"  Output Signal '{signal}':")
                    for diff in diffs:
                        print(f"    {diff}")
            else:
                print(f"Condition '{condition.get('name', 'Unnamed')}' Passed.")
        else:
            # 读取 JSON 文件
            with open(result_json_file, "r") as f:
                result_json = json.load(f)

            # 只选择可以转换为整数的键进行排序
            step_keys = [key for key in result_json.keys() if key.isdigit()]
            sorted_step_keys = sorted(step_keys, key=int)

            # 遍历每一个时钟周期
            for step in sorted_step_keys:
                step_data = result_json[step]

                # 提取实际信号值
                actual_signals = {}
                for signal, values in step_data.items():
                    if isinstance(values, dict):
                        bin_value = values.get("Bin")
                        actual_signals[signal] = bin_value
                    else:
                        actual_signals[signal] = None

                # 对比期望和实际信号
                output_differences = {}
                for signal, expected_value_bin in condition.get(
                    "expected_output_signals", {}
                ).items():
                    signal += "_t"  # 根据你的逻辑加上 "_t"
                    actual_value = actual_signals.get(signal)
                    if actual_value is not None:
                        # Compare bits
                        differences = compare_bits(actual_value, expected_value_bin)
                        if differences:
                            output_differences[signal] = differences
                    else:
                        output_differences[signal] = ["Signal not found in results"]

                # 输出差异报告
                if output_differences:
                    print(
                        f"Step {step}, Condition '{condition.get('name', 'Unnamed')}' Failed:"
                    )
                    for signal, diffs in output_differences.items():
                        print(f"  Output Signal '{signal}':")
                        for diff in diffs:
                            print(f"    {diff}")
                else:
                    print(
                        f"Step {step}, Condition '{condition.get('name', 'Unnamed')}' Passed."
                    )

    else:
        print(f"Result JSON file '{result_json_file}' not found.")


def copy_result_json(result_json_file, output_dir, condition):
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"[E]Unable to create output directory '{output_dir}'：{e}")
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
            differences.append(
                f"Bit {bit_pos}: Actual {actual_bit}, Expected {expected_bit}"
            )
    return differences


def run_yosys(
    run_ys_file: str,
    verilog_file: str,
    result_json_file_temp: str,
    top_module: str,
    condition: list,
    result_folder: str,
):
    run_yosys_sat(
        run_ys_file, verilog_file, result_json_file_temp, top_module, condition
    )
    copy_result_json(result_json_file_temp, result_folder, condition)


if __name__ == "__main__":
    run_ys_file = "a.ys"
    config_json_file = "condition_if.json"
    verilog_file = "code(1).v"
    result_json_file_temp = "result_temp.json"
    result_folder = "Result"

    top_module, conditions = parse_config(config_json_file)

    for condition in conditions:
        run_yosys_sat(
            run_ys_file, verilog_file, result_json_file_temp, top_module, condition
        )
        copy_result_json(result_json_file_temp, result_folder, condition)
