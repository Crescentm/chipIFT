from collections.abc import Iterable
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

    def __init__(self, term_list: list) -> None:
        self.term_list = term_list

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
        rtag = self._traverse_subtree(rval, name_list)

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
        if type(node) is vast.Identifier:
            if node.name in name_list:

                node.name = f"{node.name}_t"
        children = node.children()
        if type(children) is tuple:
            for child in children:
                self._do_replace_name(child, name_list)

    def _traverse_subtree(self, node: vast.Rvalue, name_list: tuple) -> vast.Rvalue:
        new_var = self._do_traverse_subtree(node.var, name_list)
        new_node = vast.Rvalue(var=new_var)
        return new_node

    def _do_traverse_subtree(self, node: vast.Node, name_list: tuple) -> vast.Node:
        children = node.children()
        children_tags = []
        if type(children) is tuple:
            for child in children:
                child_tag = self._do_traverse_subtree(child, name_list)
                children_tags.append(child_tag)

        if isinstance(node, vast.Operator):
            new_node = ift.rule_set[type(node)](children, children_tags).gen_rule()
        elif type(node) is vast.Identifier:
            if node.name in name_list:
                new_node = vast.Identifier(name=f"{node.name}_t")
            else:
                new_node = copy.deepcopy(node)
        elif isinstance(node, vast.Constant):
            new_node = type(node)(value=0)
        else:
            # TODO: copy the logic
            pass
        return new_node
