import json
import subprocess
import sys
import os


def run_yosys(run_ys_file, config_json_file, verilog_file, result_json_file):
    with open(config_json_file, "r") as f:
        config = json.load(f)

    ys_script = []

    ys_script.append(f"read_verilog {verilog_file}")

    ys_script.append(f"hierarchy -top {config['top_module']}")

    ys_script.append("proc; opt; flatten")

    sat_cmd = "sat"

    if "set" in config["sat_options"]:
        for signal, value in config["sat_options"]["set"].items():
            sat_cmd += f" -set {signal} {value}"

    if "show" in config["sat_options"]:
        for signal in config["sat_options"]["show"]:
            sat_cmd += f" -show {signal}"

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

    # print(result.stdout)

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

        # XXX： Never in?
        input_differences = {}
        for signal, expected_value in config.get("input_signals", {}).items():
            actual_value = actual_signals.get(signal)
            if actual_value is not None:
                expected_value_bin = format(expected_value, f"0{len(actual_value)}b")
                differences = compare_bits(actual_value, expected_value_bin)
                if differences:
                    input_differences[signal] = differences

        output_differences = {}
        for signal, expected_value in config.get("expected_output_signals", {}).items():
            actual_value = actual_signals.get(signal)
            if actual_value is not None:
                expected_value_bin = format(expected_value, f"0{len(actual_value)}b")
                differences = compare_bits(actual_value, expected_value_bin)
                if differences:
                    output_differences[signal] = differences

        if input_differences or output_differences:
            print("Fail at：")
            for signal, diffs in input_differences.items():
                for diff in diffs:
                    print(f"{signal}{diff}")

            for signal, diffs in output_differences.items():
                for diff in diffs:
                    print(f"{signal}{diff}")
        else:
            print("Pass.")
    else:
        print(f"Result not found.")


def compare_bits(actual_value, expected_value):
    differences = []
    max_len = max(len(actual_value), len(expected_value))
    actual_value = actual_value.zfill(max_len)
    expected_value = expected_value.zfill(max_len)

    for i in range(max_len):
        bit_pos = max_len - i  # 位位置，从高位到低位
        actual_bit = actual_value[i]
        expected_bit = expected_value[i]
        if actual_bit != expected_bit:
            differences.append(f"[{bit_pos}] = {expected_bit}")
    return differences


if __name__ == "__main__":
    p = [
        "/tmp/tmp-fc8b7c5d455ab89d8a492ba540c540a57db8584ccaa2353d6be74b25bfef4799-chipift/a.ys",
        "tests/config.json",
        "/tmp/tmp-fc8b7c5d455ab89d8a492ba540c540a57db8584ccaa2353d6be74b25bfef4799-chipift/code.v",
        "./result.json",
    ]
    run_yosys(p[0], p[1], p[2], p[3])
