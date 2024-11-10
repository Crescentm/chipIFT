import pyverilog.vparser.ast as vast
import inspect


class TaintVar:
    def __init__(self, var_name: str, module_type: str, value) -> None:
        self.var_name = var_name
        self.module_type = module_type
        self.value = value

    def __repr__(self) -> str:
        return f"{self.var_name}:{self.module_type}"


class Preprocess:

    def __init__(self, _ast, _module_list, taint_var) -> None:
        self._ast: vast.Source = _ast
        self._module_list = _module_list
        self._module_num = len(_module_list)
        self.taint_var: list[tuple[str, str]] = taint_var

        self.conditions_dicts: list[dict[int, list]] = []
        self.current_module_index = 0
        self.term_list = []

    def traverse(self):
        self.conditions_dict: dict[int, list] = {}
        self.current_conditions = []
        for module_index in range(self._module_num):
            self.current_module_index = module_index
            ports: vast.Port = self._ast.description.definitions[
                module_index
            ].portlist.ports
            self._traverse_node(ports)
            items = self._ast.description.definitions[module_index].items
            self._traverse_node(items)
            self.conditions_dicts.append(self.conditions_dict)

        return self.conditions_dicts

    def _traverse_node(self, node) -> None:
        if not isinstance(node, tuple):
            children = (node,)
        else:
            children = node

        for child in children:
            match type(child):
                case (
                    vast.Assign
                    | vast.Substitution
                    | vast.NonblockingSubstitution
                    | vast.BlockingSubstitution
                ):
                    self.conditions_dict[child.lineno] = self.current_conditions
                case vast.IfStatement:
                    self.current_conditions.append(child.cond)
                    self._traverse_node(child.true_statement)
                    self._traverse_node(child.false_statement)
                    self.current_conditions.pop()
                case vast.CaseStatement:
                    for case in child.caselist:
                        self.current_conditions.append(vast.Eql(child.comp, case.cond))
                        self._traverse_node(case.statement)
                        self.current_conditions.pop()
                case vast.CasexStatement | vast.CasezStatement:
                    for case in child.caselist:
                        self.current_conditions.append(vast.Eq(child.comp, case.cond))
                        self._traverse_node(case.statement)
                        self.current_conditions.pop()
                case (
                    vast.Variable
                    | vast.Port
                    | vast.Input
                    | vast.Output
                    | vast.Inout
                    | vast.Wire
                    | vast.Reg
                    | vast.Integer
                    | vast.Real
                    | vast.Genvar
                ):
                    if (
                        child.name,
                        self._module_list[self.current_module_index],
                    ) in self.taint_var:
                        self.term_list.append(
                            TaintVar(
                                child.name,
                                self._module_list[self.current_module_index],
                                child,
                            )
                        )
                case (
                    vast.Always
                    | vast.AlwaysFF
                    | vast.AlwaysComb
                    | vast.AlwaysLatch
                    | vast.GenerateStatement
                    | vast.Block
                    | vast.WhileStatement
                    | vast.ForStatement
                    | vast.Partselect
                    | vast.Repeat
                    | vast.Ioport
                    | vast.Decl
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
                    for _, value in param_values.items():
                        self._traverse_node(value)
                case _:
                    return
