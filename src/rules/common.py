import pyverilog.vparser.ast as vast
import src.rules.ift as ift
import copy


"""
Generate IFT snippet
"""


class FlowTracker(object):
    assignment_operator = (
        vast.Assign,
        vast.NonblockingSubstitution,
        vast.BlockingSubstitution,
    )

    def __init__(self, term_list: list, conditions: list = []) -> None:
        self.term_list = term_list
        self.conditions = conditions

    """
    process generate
    """

    def track_flow(self, node: vast.Node, module_name: str) -> vast.Node:
        name_list = tuple(_[0] for _ in self.term_list if _[1] == module_name)
        assert type(node) in self.assignment_operator
        if type(node) is vast.Assign:
            lval = node.left
            rval = node.right
        elif isinstance(node, vast.Substitution):
            lval = node.left
            rval = node.right
        else:
            raise TypeError  # XXX

        ltag = self._replace_name(lval, name_list)
        # TODO: check wether lval is in conditions
        rtag = self._track_rval(rval, name_list, False)  # TODO: change me later

        match type(node):
            case vast.Assign:
                new_node = vast.Assign(left=ltag, right=rtag)
            case vast.NonblockingSubstitution:
                new_node = vast.NonblockingSubstitution(left=ltag, right=rtag)
            case vast.BlockingSubstitution:
                new_node = vast.BlockingSubstitution(left=ltag, right=rtag)
        return new_node

    def _replace_name(self, node: vast.Lvalue, name_list: tuple) -> vast.Lvalue:
        new_node = copy.deepcopy(node)
        self._do_replace_name(new_node, name_list)
        return new_node

    def _do_replace_name(self, node: vast.Node, name_list: tuple) -> None:
        match type(node):
            case vast.Identifier:
                if node.name in name_list:
                    node.name = f"{node.name}_t"
            case vast.Partselect:
                self._do_replace_name(node.var, name_list)
                return
            case vast.Pointer:
                self._do_replace_name(node.var, name_list)
                return
        # else
        children = node.children()
        if type(children) is tuple:
            for child in children:
                self._do_replace_name(child, name_list)

    def _track_rval(
        self, node: vast.Rvalue, name_list: tuple, have_imp=False
    ) -> vast.Rvalue:
        exp_ift = self._traverse_subtree(node.var, name_list)
        if have_imp:
            imp_ift = self._implicit_ift()
            new_var = vast.Or(left=exp_ift, right=imp_ift)
        else:
            new_var = exp_ift
        new_node = vast.Rvalue(var=new_var)
        return new_node

    def _traverse_subtree(
        self,
        node: vast.Node,
        name_list: tuple,
    ) -> vast.Node:

        children = node.children()
        children_tags = []
        if type(children) is tuple:
            for child in children:
                child_tag = self._traverse_subtree(
                    child,
                    name_list,
                )
                children_tags.append(child_tag)

        if isinstance(node, vast.Operator):
            if type(node) in ift.rule_set:
                op_ift = ift.rule_set[type(node)]
                new_node = op_ift(children, children_tags).gen_rule()
            else:
                new_node = ift.OperatorIFT().gen_rule()
        elif isinstance(node, vast.Constant):
            new_node = type(node)(value="0")
        else:
            match type(node):
                case vast.Identifier:
                    if node.name in name_list:
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

    def _implicit_ift(self) -> vast.Node:
        return vast.IntConst(value="0")  # TODO: change me later
