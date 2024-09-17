import sys
import os
import pyverilog
import pyverilog.vparser.ast as vast
from optparse import OptionParser
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from pyverilog.vparser.parser import parse


def main():
    INFO = "Verilog code parser"
    VERSION = pyverilog.__version__
    USAGE = "Usage: python example_parser.py file ..."

    def showVersion():
        print(INFO)
        print(VERSION)
        print(USAGE)
        sys.exit()

    optparser = OptionParser()
    optparser.add_option(
        "-v",
        "--version",
        action="store_true",
        dest="showversion",
        default=False,
        help="Show the version",
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
    (options, args) = optparser.parse_args()

    filelist = args
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()

    ast, _ = parse(
        filelist, preprocess_include=options.include, preprocess_define=options.define
    )

    # module_defs is a tuple of ModuleDefs.
    module_defs: tuple = ast.children()[0].children()

    # try the first module.
    module_def: vast.ModuleDef = module_defs[0]
    items = module_def.items
    # print(type(items))
    codegen = ASTCodeGenerator()
    rslt = codegen.visit(ast)
    print(rslt)


if __name__ == "__main__":
    main()
