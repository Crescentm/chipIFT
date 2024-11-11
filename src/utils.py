import pyverilog.vparser.ast as vast
import pyverilog.dataflow.dataflow as vdfg
from enum import Enum
import os

dfop_mark = {
    "Uminus": vast.Uminus,
    "Ulnot": vast.Ulnot,
    "Unot": vast.Unot,
    "Uand": vast.Uand,
    "Unand": vast.Unand,
    "Uor": vast.Uor,
    "Unor": vast.Unor,
    "Uxor": vast.Uxor,
    "Uxnor": vast.Uxnor,
    "Power": vast.Power,
    "Times": vast.Times,
    "Divide": vast.Divide,
    "Mod": vast.Mod,
    "Plus": vast.Plus,
    "Minus": vast.Minus,
    "Sll": vast.Sll,
    "Srl": vast.Srl,
    "Sla": vast.Sla,
    "Sra": vast.Sra,
    "LessThan": vast.LessThan,
    "GreaterThan": vast.GreaterThan,
    "LessEq": vast.LessEq,
    "GreaterEq": vast.GreaterEq,
    "Eq": vast.Eq,
    "NotEq": vast.NotEq,
    "Eql": vast.Eql,
    "NotEql": vast.NotEql,
    "And": vast.And,
    "Xor": vast.Xor,
    "Xnor": vast.Xnor,
    "Or": vast.Or,
    "Land": vast.Land,
    "Lor": vast.Lor,
}

const_mark = {
    vdfg.DFIntConst: vast.IntConst,
    vdfg.DFFloatConst: vast.FloatConst,
    vdfg.DFStringConst: vast.StringConst,
}


def file_exists(file_list: list):
    if len(file_list) == 0:
        return None

    for f in file_list:
        if not os.path.exists(f):
            raise IOError("[E] file not found: " + f)


def dfnode_2_astnode(dfnode):
    match type(dfnode):
        case vdfg.DFOperator:
            if len(dfnode.nextnodes) == 1:
                ret = dfnode_2_astnode(dfnode.nextnodes[0])
                return dfop_mark[dfnode.operator](right=ret)  # type: ignore
            elif len(dfnode.nextnodes) == 2:
                retl = dfnode_2_astnode(dfnode.nextnodes[0])
                retr = dfnode_2_astnode(dfnode.nextnodes[1])
                return dfop_mark[dfnode.operator](left=retl, right=retr)  # type: ignore
            else:
                raise ValueError("[E] Invalid number of operands")
        case vdfg.DFIntConst | vdfg.DFFloatConst | vdfg.DFStringConst:
            ret = dfnode.eval()
            return const_mark[type(dfnode)](str(ret))
        case vdfg.DFTerminal:
            return vast.Identifier(dfnode.name[-1:].tocode())
        case vdfg.DFEvalValue:
            if dfnode.isstring:
                return vast.StringConst(dfnode.value)
            elif dfnode.isfloat:
                return vast.FloatConst(dfnode.value)
            else:
                return vast.IntConst(dfnode.value)
        case _:
            print("[E]Unknown type: ", type(dfnode))
            return dfnode


class DeclType(Enum):
    REG = 1
    WIRE = 2


def new_decl(decltype: DeclType, name: list[str], **args) -> vast.Decl:
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

    else:
        raise ValueError("[E] Invalid declaration type")


def taint_variable(child: vast.Variable):
    pass
