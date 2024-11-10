from src.utils import file_exists
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer
import pyverilog.utils.scope as vscope
import pyverilog.dataflow.dataflow as vdfg
from pyverilog.dataflow.dataflow_codegen import VerilogCodeGenerator
from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer


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

    def gen_taint_vars(self) -> list[tuple[str, str]]:
        taint_var = []
        instance_dict = dict(self.instances)
        for value in self.terms.values():
            var_name = str(value.name[-1:])
            module_type = instance_dict[value.name[:-1]]
            taint_var.append((var_name, module_type))

        return taint_var
