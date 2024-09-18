from copy import deepcopy
from types import new_class
import pyverilog
import pyverilog.dataflow.dataflow as vdfg
import pyverilog.vparser.ast as vast
from pyverilog.vparser.parser import Source
from ast_verilog import DFGVerilog
from rules.rules import VerilogOperator
import copy

def track_flow(node: vast.Node) -> vast.Node:
    pass

class FlowTracker(object):
    assignment_kw = (
            "assign"
            )
    volatile_variables = (
            vast.Reg,
            vast.Wire,
            vast.Tri
            )
    def __init__(self, ast: vast.Source, cfg) -> None:
        self.ast: vast.Source = ast
        self.cfg = cfg
        self.result = dict()

    def tracking(self) -> None:
        pass

    def _list_modules(self, source: vast.Source) -> list:
        modules = []
        for description in source.children():
            module_defs = list(description.children())
            modules += module_defs
        return modules

    def _track_module(self, module: vast.ModuleDef) -> None:
        changes_in_module = []
        port_tags = []
        decl_tags = []
        for child in module.children():
            match type(child):
                case vast.Portlist:
                    self._add_port_tags(child)
                case vast.Paramlist:
                    pass
                case vast.Decl:
                    self._add_decl_tag(child)
                case vast.InstanceList:
                    self._modify_instance(child)
                case _:
                    pass

    def _add_port_tags(self, portlist: vast.Portlist) -> list:
        tags = []
        for ioport in portlist.children(): # "copy" each port
            assert(type(ioport) is vast.Ioport)
            # first
            first = copy.deepcopy(ioport.first)
            first.name = f"{first.name}_t"
            # second
            if ioport.second:
                second = copy.deepcopy(ioport.second)
                second.name = f"{second.name}_t"
            else:
                second = None
            new_port = vast.Ioport(first=first, second=second)
            tags.append(new_port)
        return tags

    def _add_decl_tag(self, decl: vast.Decl) -> list:
        tags = []
        for child in decl.children():
            # assert(type(child) is vast.Variable)
            if type(child) in self.volatile_variables:
                pass
        return tags

    def _modify_instance(self, instance_list: vast.InstanceList) -> None:
        pass


