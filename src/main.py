import sys
import os
import hashlib
import time
import argparse
from src import run_yosys
from src.ast_verilog import ASTVerilog
from src.run_yosys import parse_config, run_yosys

CODE_FILE = "code.v"
YS_FILE = "a.ys"
RESULT_FILE = "result.json"


def generate_tmp_pathname() -> str:
    h = hashlib.sha256()
    h.update(str(time.time()).encode("utf-8"))
    hashval = h.hexdigest()[:10]
    return f"/tmp/tmp-{hashval}-chipift"


def get_parser():

    parser = argparse.ArgumentParser(description="ChipIFT - A tool for Verilog IFT")

    parser.add_argument(
        "-v",
        "--version",
        dest="showversion",
        action="store_true",
        default=False,
        help="Show the version",
    )

    parser.add_argument(
        "-f",
        "--files",
        dest="filelist",
        nargs="+",
        action="store",
        default=[],
        help="Source code list",
    )

    parser.add_argument(
        "-c",
        "--condition",
        dest="path_to_condition",
        action="store",
        default="./config.json",
        help="Condition file",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="result_path",
        action="store",
        default="./result.json",
        help="result directory",
    )

    parser.add_argument(
        "-I",
        "--include",
        dest="include",
        action="store",
        default=[],
        help="Include path",
        nargs="+",
    )

    parser.add_argument(
        "-D",
        dest="define",
        action="store",
        default=[],
        help="Macro Definition",
        nargs="+",
    )

    parser.add_argument(
        "-t",
        "--time",
        dest="time_flag",
        action="store_true",
        default=False,
        help="Collect time overhead",
    )

    return parser


def main():
    INFO = "ChipIFT"
    VERSION = 0.1

    def showversion():
        print(f"{INFO} {VERSION}")
        sys.exit()

    parser = get_parser()
    options = parser.parse_args()

    if options.showversion:
        showversion()
        exit()

    if len(options.filelist) <= 0:
        parser.print_help()
        exit()

    # save temp files
    tmp_path = generate_tmp_pathname()
    os.mkdir(tmp_path)
    tmp_code_path = f"{tmp_path}/{CODE_FILE}"
    tmp_ys_path = f"{tmp_path}/{YS_FILE}"
    tmp_result_path = f"{tmp_path}/{RESULT_FILE}"

    for f in options.filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    # check wether result path exists
    start_time = time.time()
    top_module, conditions = parse_config(options.path_to_condition)
    ast = ASTVerilog(
        options.filelist,
        include_list=options.include,
        topmodule=top_module,
    )

    for i in range(ast.module_num):
        ast.traverse_modify_ast(module_index=i)

    if options.time_flag:
        finish_traverse_time = time.time()
        print(f"[I] Finish Modifying AST: {finish_traverse_time - start_time}")

    modified_code = ast.gen_code()
    with open(tmp_code_path, "w") as f:
        f.write(modified_code)

    if options.time_flag:
        codegen_time = time.time()
        print(f"[I] Finish code generation: {codegen_time - start_time}")

    for condition in conditions:
        run_yosys(
            run_ys_file=tmp_ys_path,
            verilog_file=tmp_code_path,
            result_json_file_temp=tmp_result_path,
            top_module=top_module,
            condition=condition,
            result_folder=options.result_path,
        )
    if options.time_flag:
        end_time = time.time()
        print(f"[I] Finish SAT: {end_time - start_time}")


if __name__ == "__main__":
    main()
