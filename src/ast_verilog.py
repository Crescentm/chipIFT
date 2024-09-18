from pyverilog.vparser.parser import parse
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from pyverilog.dataflow.dataflow_codegen import VerilogCodeGenerator
from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer
from enum import Enum
import pyverilog.dataflow.dataflow as vdfg
import pyverilog.utils.scope as vscope
import pyverilog.vparser.ast as vast
import os


def file_exists(file_list: list):
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
        self.directives: tuple = analyzer.get_directives()
        self.instances: tuple = analyzer.getInstances()
        self.terms: dict[vscope.ScopeChain, vdfg.Term] = analyzer.getTerms()
        self.binddict: dict[vscope.ScopeChain, list[vdfg.Bind]] = analyzer.getBinddict()
        self.constlist = analyzer.getConsts()

        self.topmodule = topmodule

    def gen_code(
        self,
        clockname: str = "CLK",
        resetname: str = "RST_X",
        clockedge: str = "posedge",
        resetedge: str = "negedge",
        searchtarget=[],
    ):
        # Need to solve
        # module 'pyverilog.utils.signaltype' has no attribute 'isWireArray'
        optimizer = VerilogDataflowOptimizer(self.terms, self.binddict)
        optimizer.resolveConstant()
        resolved_terms = optimizer.getResolvedTerms()
        resolved_binddict = optimizer.getResolvedBinddict()
        constlist = optimizer.getConstlist()
        codegen = VerilogCodeGenerator(
            self.topmodule,
            self.terms,
            self.binddict,
            resolved_terms,
            resolved_binddict,
            constlist,
        )
        codegen.set_clock_info(clockname, clockedge)
        codegen.set_reset_info(resetname, resetedge)
        code = codegen.generateCode()
        return code


class DeclType(Enum):
    REG = 1
    WIRE = 2


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

        self.parser = ast
        self.source: vast.Source = ast
        self.module_num = len(ast.children()[0].children())

    def show(self):
        self.parser.show()

    def new_decl(self, decltype: DeclType, name: list[str], **args) -> vast.Decl:
        """
        new_decl: Create one new declaration\n
        decltype: Type of declaration;
        name: Name of the declaration, a list of strings;
        [width]: Width of the declaration, a list of tuples;
        """
        decl = []
        if decltype == DeclType.REG:
            width: tuple = args["width"]
            for index in range(len(name)):
                decl.append(
                    vast.Reg(
                        name[index],
                        width=vast.Width(
                            vast.IntConst(str(width[0])),
                            vast.IntConst(str(width[1])),
                        ),
                    )
                )
            return vast.Decl(tuple(decl))

        elif decltype == DeclType.WIRE:
            for index in range(len(name)):
                decl.append(vast.Wire(name[index]))

            return vast.Decl(tuple(decl))

    def add_decls(self, delcs: list[vast.Decl], module_index: int = 0):
        module: vast.ModuleDef = self.source.description.definitions[module_index]
        items = tuple(delcs + list(module.items))

        module_new = vast.ModuleDef(
            module.name, module.paramlist, module.portlist, items
        )

        module_list = list(self.source.description.definitions)
        module_list[module_index] = module_new
        self.source.description.definitions = tuple(module_list)

        return True

    def gen_code(self):
        codegen = ASTCodeGenerator()
        rslt = codegen.visit(self.source)
        return rslt


class VerilogParser:

    def __init__(
        self, file_list, include_list: list = [], define_list: list = []
    ) -> None:
        self.file_list: list = file_list
        self.include_list: list = include_list
        self.define_list: list = define_list
        self.ast: ASTVerilog = ASTVerilog(file_list, include_list, define_list)
        self.dfg: DFGVerilog = DFGVerilog(
            file_list, include_list=include_list, define_list=define_list
        )  # Just ignore the other args


def decl_add_example():
    file_list = ["./tests/test.v"]
    ast = ASTVerilog(file_list)
    decl1 = ast.new_decl(decltype=DeclType.REG, name=["a", "b"], width=(31, 0))
    decl2 = ast.new_decl(decltype=DeclType.WIRE, name=["a_t", "b_t"], width=(31, 0))
    ast.add_decls([decl1, decl2])
    print(ast.gen_code())


if __name__ == "__main__":
    decl_add_example()
