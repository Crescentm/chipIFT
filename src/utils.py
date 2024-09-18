import pyverilog.vparser.ast as vast
from enum import Enum
import os


def file_exists(file_list: list):
    if len(file_list) == 0:
        return None

    for f in file_list:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)


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
        raise ValueError("Invalid declaration type")


def taint_variable(child: vast.Variable):
    pass
