import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ast_verilog import ASTVerilog

cases = [
    ["verilogcode/logical.v"],
    ["verilogcode/equality.v"],
    ["verilogcode/relational.v"],
]


def test_gencode(filelist):
    ast = ASTVerilog(filelist)
    for i in range(ast.module_num):
        ast.traverse_modify_ast(i)
    print(ast.gen_code())


for case in cases:
    test_gencode(case)
