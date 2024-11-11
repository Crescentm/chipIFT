from src.utils import *
from src.rules.common import *
from pyverilog.vparser.parser import parse
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
from src.dfg_verilog import DFGVerilog
from src.preprocessor import Preprocessor, TaintVar
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

        preprocess = Preprocessor(
            ast,
            [module.name for module in ast.description.definitions],
        )
        preprocess.traverse()

        self.terms_list = preprocess.term_list
        self.file_list = file_list
        self.include_list = include_list
        self.define_list = define_list
        self.source: vast.Source = ast
        self.module_num = len(ast.children()[0].children())
        self.module_name_list = [module.name for module in ast.description.definitions]
        self.conditions_dicts: list[dict[int, list[vast.Node]]] = (
            preprocess.conditions_dicts
        )

    def show(self):
        self.source.show()

    def gen_code(self):
        codegen = ASTCodeGenerator()
        rslt = codegen.visit(self.source)
        return rslt

    def traverse_modify_ast(self, module_index: int = 0):
        module: vast.ModuleDef = self.source.description.definitions[module_index]
        module_list = list(self.source.description.definitions)
        flow_tracker = FlowTracker(term_list=self.terms_list)

        def traverse(node, addBlock=False):
            # node may be a tuple or a single node
            if not isinstance(node, tuple):
                children = (node,)
            else:
                children = node
            children_new = []
            for child in children:
                match type(child):
                    case vast.Port:
                        children_new.append(child)
                        taint_port = copy.deepcopy(child)
                        taint_port.name = f"{taint_port.name}_t"
                        children_new.append(taint_port)
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
                        cond: list[vast.Node] | None = self.conditions_dicts[
                            module_index
                        ].get(child.lineno)
                        if cond:
                            ret = flow_tracker.track_flow(child, module.name, cond)
                        else:
                            ret = flow_tracker.track_flow(child, module.name)
                        children_new.append(child)
                        if ret:
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
                                if taint_port.portname is not None:
                                    taint_port.portname = f"{port.portname}_t"
                                new_ports.append(port)
                                new_ports.append(taint_port)
                            elif isinstance(port, vast.PortArg) and isinstance(
                                port.argname, vast.Constant
                            ):
                                taint_port = copy.deepcopy(port)
                                if taint_port.portname is not None:
                                    taint_port.portname = f"{port.portname}_t"
                                taint_port.argname = vast.IntConst("0")
                                new_ports.append(port)
                                new_ports.append(taint_port)
                            else:
                                new_ports.append(port)

                        children_new.append(
                            vast.Instance(
                                child.module, child.name, new_ports, child.parameterlist
                            )
                        )
                    case vast.IfStatement:
                        match type(child.true_statement):
                            case (
                                vast.Assign
                                | vast.Substitution
                                | vast.BlockingSubstitution
                                | vast.NonblockingSubstitution
                            ):
                                if child.true_statement is not None:
                                    true_statement = vast.Block(
                                        traverse(child.true_statement, addBlock=True)
                                    )
                                else:
                                    true_statement = None

                                if child.false_statement is not None:
                                    false_statement = vast.Block(
                                        traverse(child.false_statement, addBlock=True)
                                    )
                                else:
                                    false_statement = None
                            case _:
                                true_statement = traverse(child.true_statement)
                                false_statement = traverse(child.false_statement)
                        children_new.append(
                            vast.IfStatement(
                                child.cond, true_statement, false_statement
                            )
                        )
                    case vast.Case:
                        match type(child.statement):
                            case (
                                vast.Assign
                                | vast.Substitution
                                | vast.BlockingSubstitution
                                | vast.NonblockingSubstitution
                            ):
                                statement = vast.Block(
                                    traverse(child.statement, addBlock=True)
                                )
                            case _:
                                statement = traverse(child.statement)
                        children_new.append(vast.Case(child.cond, statement))

                    case (
                        vast.Decl
                        | vast.Concat
                        | vast.SensList
                        | vast.Portlist
                        | vast.Always
                        | vast.AlwaysFF
                        | vast.AlwaysComb
                        | vast.AlwaysLatch
                        | vast.Width
                        | vast.GenerateStatement
                        | vast.Block
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
                    case (
                        vast.Constant
                        | vast.IntConst
                        | vast.FloatConst
                        | vast.StringConst
                    ):
                        children_new.append(child)
                    case _:
                        children_new.append(child)

            if not isinstance(node, tuple) and addBlock == False:
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
