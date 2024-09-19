import pyverilog
import pyverilog.vparser.ast as vast
from pyverilog.vparser.parser import parse
from optparse import OptionParser
import sys
import os

from pyverilog.vparser.preprocessor import preprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import src.rules.common as common

cases = {
    "and": (
        ["verilogcode/and.v"],  # filelist
        [
            ("x", "bitwiseand", ("Wire", "Input")),
            ("y", "bitwiseand", ("Wire", "Input")),
            ("o", "bitwiseand", ("Wire", "Output")),
        ],  # termlist
        lambda ast: ast.description.definitions[0].items[0],  # path to block
        "bitwiseand",  # top module name
    ),
}


def test(thiscase: tuple):
    filelist = thiscase[0]
    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)
    ast, directives = parse(filelist, preprocess_include=[], preprocess_define=[])
    # ast.show()
    for lineno, directive in directives:
        print("Line %d : %s" % (lineno, directive))
    thiscase[2](ast).show()
    result = common.FlowTracker(thiscase[1]).track_flow(thiscase[2](ast), thiscase[3])
    # result.show()


# define test
test(cases["and"])
