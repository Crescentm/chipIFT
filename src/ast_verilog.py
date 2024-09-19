import pprint
from pyverilog.vparser.parser import parse
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from pyverilog.dataflow.dataflow_codegen import VerilogCodeGenerator
from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer
from src.utils import *
from src.rules.common import *
import copy
import pyverilog.dataflow.dataflow as vdfg
import pyverilog.utils.scope as vscope
import pyverilog.vparser.ast as vast


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
        """
        DO NOT USE THIS !\n
        Need to solve: module 'pyverilog.utils.signaltype' has no attribute 'isWireArray'
        """
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

    def gen_taint_vars(self):
        taint_var = []
        instance_dict = dict(self.instances)
        for value in self.terms.values():
            var_name = str(value.name[-1:])
            module_type = instance_dict[value.name[:-1]]
            var_type = tuple(value.termtype)
            taint_var.append((var_name, module_type, var_type))

        return taint_var


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

        self.file_list = file_list
        self.parser = ast
        self.source: vast.Source = ast
        self.module_num = len(ast.children()[0].children())
        self.module_name_list = [module.name for module in ast.description.definitions]

    def show(self):
        self.parser.show()

    def gen_code(self):
        codegen = ASTCodeGenerator()
        rslt = codegen.visit(self.source)
        return rslt

    def traverse_modify_ast(self, module_index: int = 0):
        module: vast.ModuleDef = self.source.description.definitions[module_index]
        module_list = list(self.source.description.definitions)
        dfg = DFGVerilog(self.file_list, topmodule=module.name)
        terms_list = dfg.gen_taint_vars()
        flow_tracker = FlowTracker(term_list=terms_list)

        def traverse(node):
            children: tuple = node.children()
            children_new = []
            if len(children) == 0:
                return ()
            for child in children:
                match type(child):
                    case vast.Portlist | vast.Decl | vast.Concat | vast.SensList:
                        ret = traverse(child)
                        children_new.append(type(child)(ret))
                    case vast.Ioport:
                        children_new.append(child)
                        # TODO: if Input/Output/Inout have nested structure
                        if (child.first != None) | (child.second != None):
                            taint_ioport: vast.Ioport = copy.deepcopy(child)
                            if isinstance(taint_ioport.first, vast.Variable):
                                taint_ioport.first.name = f"{child.first.name}_t"
                            if isinstance(taint_ioport.second, vast.Variable):
                                taint_ioport.second.name = f"{child.second.name}_t"
                            children_new.append(taint_ioport)
                    case vast.Tri | vast.Wire | vast.Reg:
                        children_new.append(child)
                        taint_var: vast.Reg = copy.deepcopy(child)
                        taint_var.name = f"{taint_var.name}_t"
                        children_new.append(taint_var)
                    case vast.Assign:
                        children_new.append(child)
                        ret = flow_tracker.track_flow(child, module.name)
                        children_new.append(ret)
                    case (
                        vast.Constant
                        | vast.IntConst
                        | vast.FloatConst
                        | vast.StringConst
                    ):
                        children_new.append(child)
                    case _:
                        children_new.append(child)
            return tuple(children_new)

        ret = traverse(module)
        module_list[module_index] = vast.ModuleDef(module.name, ret[0], ret[1], ret[2:])  # type: ignore
        self.source.description.definitions = tuple(module_list)


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


def tarverse_example():
    file_list = ["./verilogcode/and.v"]
    ast = ASTVerilog(file_list)
    for i in range(ast.module_num):
        ast.traverse_modify_ast(module_index=i)
    print(ast.gen_code())


def dfg_example():
    file_list = ["./verilogcode/test2.v"]
    dfg = DFGVerilog(file_list, topmodule="top_module")
    pprint.pprint(dfg.gen_taint_vars())


def test():
    print(vast.Node)


if __name__ == "__main__":
    tarverse_example()
