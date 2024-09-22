import sys
import os
from optparse import OptionParser
import hashlib
import time

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


def main():
    INFO = "ChipIFT"
    USAGE = "chipift -f <file list> -c <conditions.json>"
    VERSION = 0.1

    def showversion():
        print(f"{INFO} {VERSION}")
        print(f"{USAGE}")
        sys.exit()

    optparser = OptionParser()
    optparser.add_option(
        "-v",
        "--version",
        dest="showversion",
        action="store_true",
        default=False,
        help="Show the version",
    )
    optparser.add_option(
        "-f",
        "--files",
        dest="filelist",
        action="append",
        default=[],
        help="Source code list",
    )
    optparser.add_option(
        "-c",
        "--condition",
        dest="path_to_condition",
        action="store",
        default="./config.json",
        help="Condition file",
    )
    optparser.add_option(
        "-o",
        "--output",
        dest="result_path",
        action="store",
        default="./result",
        help="result directory",
    )
    optparser.add_option(
        "-I",
        "--include",
        dest="include",
        action="append",
        default=[],
        help="Include path",
    )
    optparser.add_option(
        "-D", dest="define", action="append", default=[], help="Macro Definition"
    )
    # TODO: add -D and -I to ast ganerate
    (options, _) = optparser.parse_args()

    if options.showversion:
        showversion()

    if not options.filelist:
        showversion()

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

    ast = ASTVerilog(options.filelist)
    for i in range(ast.module_num):
        ast.traverse_modify_ast(module_index=i)
    modified_code = ast.gen_code()
    with open(tmp_code_path, "w") as f:
        f.write(modified_code)

    top_module, conditions = parse_config(options.path_to_condition)
    for condition in conditions:
        run_yosys(
            run_ys_file=tmp_ys_path,
            verilog_file=tmp_code_path,
            result_json_file_temp=tmp_result_path,
            top_module=top_module,
            condition=condition,
            result_folder=options.result_path
        )

if __name__ == "__main__":
    main()
