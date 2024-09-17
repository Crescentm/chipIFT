from pyverilog.vparser.parser import parse
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
import pyverilog.dataflow.dataflow as vdfg
import pyverilog.utils.scope as vscope
import pyverilog.vparser.ast as vast
import os


def file_exists(file_list: list) -> bool:
    if len(file_list) == 0:
        return None

    for f in file_list:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)


class DFGVerilog:

    def __init__(
        self,
        file_list: list,
        topmodule: str = "top",
        noreorder=False,
        nobind=False,
        include_list=[],
        define_list=[],
    ):
        file_exists(file_list)
        analyzer = VerilogDataflowAnalyzer(
            file_list, topmodule, noreorder, nobind, include_list, define_list
        )
        analyzer.generate()
        self.directives: list[vdfg.Directive] = analyzer.get_directives()
        self.instances: tuple = analyzer.getInstances()
        self.terms: dict[vscope.ScopeChain, vdfg.Term] = analyzer.getTerms()
        self.binddict: dict[vscope.ScopeChain, list[vdfg.Bind]] = analyzer.getBinddict()


class ASTVerilog:

    def __init__(
        self, file_list, include_list: list = [], define_list: list = []
    ) -> None:
        file_exists(file_list)

        ast, _ = parse(
            file_list,
            preprocess_include=include_list,
            preprocess_define=define_list,
            debug=False,
        )

        self.ast: vast.Source = ast
        self.module_num = len(self.ast.children()[0].children())
        self.modules: vast.ModuleDef = self.ast.children()[0].children()

    def decls_add(self, delcs):
        modules = self.ast.children()[0].children()
        # for now, just one module
        module: vast.ModuleDef = modules[0]
        delc_list = module.items

        last_decl_index = 0
        for i, node in enumerate(delc_list):
            if isinstance(node, vast.Decl):
                last_decl_index = i

        print(last_decl_index)

    def gen_code(self):
        pass


class VerilogParser:

    def __init__(
        self, file_list, include_list: list = [], define_list: list = []
    ) -> None:
        self.file_list: list = file_list
        self.include_list: list = include_list
        self.define_list: list = define_list
        self.ast: ASTVerilog = ASTVerilog(file_list, include_list, define_list)
        self.dfg: DFGVerilog = DFGVerilog(
            file_list, include_list, define_list
        )  # Just ignore the other args


def ast_pasrser_test():
    filelist = ["./tests/test.v"]
    ast = ASTVerilog(filelist)
    # ast.decls_add(vast.Decl("reg", vast.Identifier("a")))
    dfg: DFGVerilog = ast.dfg


if __name__ == "__main__":
    ast_pasrser_test()
