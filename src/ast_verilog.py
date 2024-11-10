from src.utils import *
from src.rules.common import *
from pyverilog.vparser.parser import parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from src.dfg_verilog import DFGVerilog
from src.preprocess import Preprocess
import pyverilog.vparser.ast as vast
import inspect
import copy


class ASTVerilog:

    def __init__(
        self,
        file_list,
        include_list: list = [],
        define_list: list = [],
        topmodule: str = "top",
    ) -> None:
        file_exists(file_list)

        ast, _ = parse(
            file_list,
            preprocess_include=include_list,
            preprocess_define=define_list,
            debug=False,
        )

        dfg = DFGVerilog(
            file_list,
            topmodule=topmodule,
            include_list=include_list,
            define_list=define_list,
        )

        preprocess = Preprocess(
            ast,
            [module.name for module in ast.description.definitions],
            dfg.gen_taint_vars(),
        )
        preprocess.traverse()

        self.terms_list = preprocess.term_list
        self.file_list = file_list
        self.include_list = include_list
        self.define_list = define_list
        self.parser = ast
        self.source: vast.Source = ast
        self.module_num = len(ast.children()[0].children())
        self.module_name_list = [module.name for module in ast.description.definitions]
        # term_dict = {}
        # for term in self.terms_list:
        #     if term_dict.get(term[1]) == None:
        #         term_dict[term[1]] = [term[0]]
        #     else:
        #         term_dict[term[1]].append(term[0])

        # self.term_dict = term_dict

    def show(self):
        self.parser.show()

    def gen_code(self):
        codegen = ASTCodeGenerator()
        rslt = codegen.visit(self.source)
        return rslt

    def traverse_modify_ast(self, module_index: int = 0):
        module: vast.ModuleDef = self.source.description.definitions[module_index]
        module_list = list(self.source.description.definitions)
        flow_tracker = FlowTracker(term_list=self.terms_list)

        def traverse(node):
            # node may be a tuple or a single node
            if not isinstance(node, tuple):
                children = (node,)
            else:
                children = node
            children_new = []
            for child in children:
                match type(child):
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
                    case (
                        vast.Assign
                        | vast.Substitution
                        | vast.NonblockingSubstitution
                        | vast.BlockingSubstitution
                    ):
                        children_new.append(child)
                        ret = flow_tracker.track_flow(child, module.name)
                        children_new.append(ret)
                    case vast.Instance:
                        new_ports = []
                        for port in child.portlist:
                            if isinstance(port, vast.PortArg) and isinstance(
                                port.argname, vast.Identifier
                            ):
                                taint_port = copy.deepcopy(port)
                                taint_port.argname = vast.Identifier(
                                    f"{port.argname.name}_t"
                                )
                                taint_port.portname = f"{port.portname}_t"
                                new_ports.append(port)
                                new_ports.append(taint_port)
                            else:
                                new_ports.append(port)

                        children_new.append(
                            vast.Instance(
                                child.module, child.name, new_ports, child.parameterlist
                            )
                        )
                    case (
                        vast.Constant
                        | vast.IntConst
                        | vast.FloatConst
                        | vast.StringConst
                    ):
                        children_new.append(child)
                    case (
                        vast.Decl
                        | vast.Concat
                        | vast.SensList
                        | vast.Portlist
                        | vast.IfStatement
                        | vast.Always
                        | vast.AlwaysFF
                        | vast.AlwaysComb
                        | vast.AlwaysLatch
                        | vast.Width
                        | vast.GenerateStatement
                        | vast.Block
                        | vast.Case
                        | vast.CaseStatement
                        | vast.CasexStatement
                        | vast.CasezStatement
                        | vast.WhileStatement
                        | vast.ForStatement
                        | vast.Partselect
                        | vast.Repeat
                        | vast.InstanceList
                    ):
                        params = [
                            param
                            for param in inspect.signature(
                                child.__class__.__init__
                            ).parameters.values()
                            if param.name != "self"
                        ]
                        param_values = {
                            param.name: getattr(child, param.name, param.default)
                            for param in params
                        }
                        for key, value in param_values.items():
                            ret = traverse(value)
                            param_values[key] = ret

                        children_new.append((child.__class__)(**param_values))
                    case _:
                        children_new.append(child)

            if not isinstance(node, tuple):
                return children_new[0]
            else:
                return tuple(children_new)

        ret1 = traverse(module.paramlist)
        ret2 = traverse(module.portlist)
        ret3 = traverse(module.items)
        module_list[module_index] = vast.ModuleDef(module.name, ret1, ret2, ret3)
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


if __name__ == "__main__":
    pass
