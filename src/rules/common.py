import pyverilog.vparser.ast as vast
import src.rules.ift as ift
import copy
from src.preprocessor import TaintVar

# TODO: proper exception?

# Generate IFT snippet
class FlowTracker(object):
    assignment_operator = (
        vast.Assign,
        vast.NonblockingSubstitution,
        vast.BlockingSubstitution,
    )

    variable_to_be_tagged = (
        vast.Input,
        vast.Output,
        vast.Inout,
        vast.Tri,
        vast.Wire,
        vast.Reg
    )

    def __init__(self, term_list: list[TaintVar]) -> None:
        self.term_list = term_list

    # process the generation
    def track_flow(self, node: vast.Node, module_name: str, conditions: list[vast.Node] = []) -> vast.Node | None:
        names = {_.var_name: _.value for _ in self.term_list if _.module_type == module_name}
        assert type(node) in self.assignment_operator
        if type(node) is vast.Assign:
            lval = node.left
            rval = node.right
        elif isinstance(node, vast.Substitution):
            lval = node.left
            rval = node.right
        else:
            raise TypeError

        ltag = self._replace_name(lval, names)  # track lvalue 
        lwidth = self._calculate_width(lval, names)
        # if not have information flow:
        if lwidth is None:
            return None
        rtag = self._track_rval(rval, lwidth, names, conditions)  # track rval

        match type(node):
            case vast.Assign:
                new_node = vast.Assign(left=ltag, right=rtag)
            case vast.NonblockingSubstitution:
                new_node = vast.NonblockingSubstitution(left=ltag, right=rtag)
            case vast.BlockingSubstitution:
                new_node = vast.BlockingSubstitution(left=ltag, right=rtag)
        return new_node



    def _calculate_width(self, node: vast.Node, names: dict) -> vast.IntConst | None:
        match type(node):
            case vast.Lvalue:
                return self._calculate_width(node.var, names)
            case vast.Identifier:
                # if not have information flow.
                id_name = node.name
                id_variable: vast.Variable = names[id_name]
                if type(id_variable) not in self.variable_to_be_tagged:
                    return None
                id_width = id_variable.width
                if id_width is not None:
                    width = str(int(id_width.msb.value) - int(id_width.lsb.value) + 1)
                    return vast.IntConst(width)
                else:
                    return vast.IntConst("1")
            case vast.Partselect:
                # TODO: dimensions
                var_id: vast.Identifier = node.var
                var_name: str = var_id.name
                var_variable: vast.Variable = names[var_name]
                if type(var_variable) not in self.variable_to_be_tagged:
                    return None
                if isinstance(node.msb, vast.Constant) and isinstance(node.lsb, vast.Constant):
                    width = str(int(node.msb.value) - int(node.lsb.value) + 1)
                    return vast.IntConst(width)
                else:
                    var_width = var_variable.width
                    if var_width is not None:
                        width = str(int(var_width.msb.value) - int(var_width.lsb.value) + 1)
                        return vast.IntConst(width)
                    else:
                        return vast.IntConst("1")
            case vast.Pointer:
                var_name: str = node.var.name
                var_variable: vast.Variable = names[var_name]
                if type(var_variable) not in self.variable_to_be_tagged:
                    return None
                var_dimensions = var_variable.dimensions
                var_width = var_variable.width
                if (var_dimensions is not None) and (var_width is not None):
                    width = str(int(var_width.msb.value) - int(var_width.lsb.value) + 1)
                    return vast.IntConst(width)
                else:
                    return vast.IntConst("1")
            case vast.LConcat:
                width_int: int = 0
                for member in node.list:
                    member_width = self._calculate_width(member, names)
                    if member_width is not None:
                        width_int += int(member_width.value)
                    else:
                        raise KeyError(f"found Integer | Real | Genvar in LConcat: {member}, {type(member), {member.lineno}}")
                return vast.IntConst(str(width_int))
            case _:
                raise KeyError(f"invalid node type in Lvalue: {node}, {type(node)}, {node.lineno}")

    # track lvalue, generate the proper tag of lvalue
    def _replace_name(self, node: vast.Lvalue, names: dict) -> vast.Lvalue:
        new_node = copy.deepcopy(node)
        self._do_replace_name(new_node, names)
        return new_node

    def _do_replace_name(self, node: vast.Node, names: dict) -> None:
        match type(node):
            case vast.Identifier:
                if node.name in names:
                    node.name = f"{node.name}_t"
            case vast.Partselect:
                self._do_replace_name(node.var, names)
                return
            case vast.Pointer:
                self._do_replace_name(node.var, names)
                return
            # If the type is not matched, it means that the node does not need to be replaced or is not a leaf node.
        children = node.children()
        if type(children) is tuple:
            for child in children:
                self._do_replace_name(child, names)

    # traverse rvalue of the expression, generate tracking rules
    def _track_rval(
            self, node: vast.Rvalue, lwidth: vast.IntConst, names: dict, conditions: list[vast.Node] = []
    ) -> vast.Rvalue:
        exp_ift = self._explicit_ift(node.var, lwidth, names)
        if conditions:
            imp_ift = self._implicit_ift(conditions, lwidth, names)
            new_var = vast.Or(left=exp_ift, right=imp_ift)
        else:
            new_var = exp_ift
        new_node = vast.Rvalue(var=new_var)
        return new_node

    # generate a tracking rule from a expression(sub-syntax-tree)
    # TODO: deal with width
    def _generate_rule(
        self,
        node: vast.Node,
        lwidth: vast.IntConst,
        names: dict,
    ) -> vast.Node:

        children = node.children()
        children_tags = []
        if isinstance(children, tuple):  # XXX: better solution?
            for child in children:
                child_tag = self._generate_rule(
                    child,
                    lwidth,
                    names,
                )
                children_tags.append(child_tag)

        if isinstance(node, vast.Operator):  # Operators
            if type(node) in ift.rule_set:
                op_ift = ift.rule_set[type(node)]
                new_node = op_ift(children, children_tags, lwidth).gen_rule()
            else:
                new_node = ift.DefaultIFT().gen_rule()
        elif isinstance(node, vast.Constant):  # Consts
            new_node = type(node)(value="0")
        else:
            match type(node):
                case vast.Identifier:
                    if node.name in names:
                        new_node = vast.Identifier(name=f"{node.name}_t")
                    else:
                        new_node = copy.deepcopy(node)
                case vast.Partselect:
                    new_node = vast.Partselect(children_tags[0], node.msb, node.lsb)
                case vast.Pointer:
                    new_node = vast.Pointer(var=children_tags[0], ptr=node.ptr)
                case vast.Repeat:
                    new_node = vast.Repeat(value=children_tags[0], times=node.times)
                    pass
                case vast.Concat:
                    new_node = vast.Concat(children_tags)
                case _:
                    new_node = vast.Node()
        return new_node

    def _explicit_ift(
        self,
        node: vast.Node,
        lwidth: vast.IntConst,
        names: dict,
    ) -> vast.Node:
        return self._generate_rule(node, lwidth, names)

    def _implicit_ift(self, conditions: list[vast.Node], lwidth: vast.IntConst, names: dict) -> vast.Node:
        # XXX: relatively impercise one:
        condition_tags = []
        for condition in conditions:
            compressed_condition = vast.Uor(condition)
            condition_tag = self._generate_rule(compressed_condition, lwidth, names)
            condition_tags.append(condition_tag)
        result = condition_tags[0]
        for condition_tag in condition_tags[1:]:
            result = vast.Or(result, condition_tag)
        
        # relatively percise one:
        # compressed_condition_0 = vast.Uor(conditions[0])
        # condition_final = compressed_condition_0
        # for condition in conditions[1:]:
        #     compressed_condition = vast.Uor(condition)
        #     condition_final = vast.And(condition_final, compressed_condition)
        # result = self._generate_rule(condition_final, lwidth, names)

        return result
