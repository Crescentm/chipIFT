from sre_compile import OPCODES
from pyverilog.ast_code_generator.codegen import Operator, Uplus
import pyverilog.vparser.ast as vast


# base
class OperatorIFT(object):
    def __init__(self, operands: list = [], operands_tags: list = []) -> None:
        self.operands = operands
        self.operands_tags = operands_tags

    def gen_rule(self) -> vast.Node:
        # print("rule not implemented yet...")
        return vast.IntConst(value="0")


# Reductions:
class UandIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        Y = 0
        Y_t = self.operands_tags[Y]
        uor_Yt = vast.Uor(right=Y_t)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        uand_Y_or_Yt = vast.Uand(right=Y_or_Yt)
        result = vast.And(left=uor_Yt, right=uand_Y_or_Yt)
        return result


class UnandIFT(OperatorIFT):
    def gen_rule(self) -> vast.Operator:
        Y = 0
        Y_t = self.operands_tags[Y]
        uor_Yt = vast.Uor(right=Y_t)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        uand_Y_or_Yt = vast.Uand(right=Y_or_Yt)
        result = vast.And(left=uor_Yt, right=uand_Y_or_Yt)
        return result


class UorIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        Y = self.operands[0]
        Y_t = self.operands_tags[0]
        uor_Yt = vast.Uor(right=Y_t)
        not_Y = vast.Unot(right=Y)
        not_Y_or_Yt = vast.Or(left=not_Y, right=Y_t)
        uand_not_Y_or_Yt = vast.Uand(right=not_Y_or_Yt)
        result = vast.And(left=uor_Yt, right=uand_not_Y_or_Yt)
        return result


class UnorIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        Y = self.operands[0]
        Y_t = self.operands_tags[0]
        uor_Yt = vast.Uor(right=Y_t)
        not_Y = vast.Unot(right=Y)
        not_Y_or_Yt = vast.Or(left=not_Y, right=Y_t)
        uand_not_Y_or_Yt = vast.Uand(right=not_Y_or_Yt)
        result = vast.And(left=uor_Yt, right=uand_not_Y_or_Yt)
        return result


class UxorIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        Y_t = self.operands_tags[0]
        uor_Yt = vast.Uor(right=Y_t)
        result = uor_Yt
        return result


class UxnorIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        Y_t = self.operands_tags[0]
        uor_Yt = vast.Uor(right=Y_t)
        result = uor_Yt
        return result


# Arithmetic
class UplusIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        return self.operands_tags[0]


class UminusIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        return self.operands_tags[0]


class PlusIFT(OperatorIFT):
    pass


class MinusIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        X = 0
        Y = 1
        X_or_Xt = vast.Or(self.operands[X], self.operands_tags[X])
        not_Yt = vast.Unot(self.operands_tags[Y])
        Y_and_not_Yt = vast.And(self.operands[Y], not_Yt)
        minus1 = vast.Minus(X_or_Xt, Y_and_not_Yt)

        not_Xt = vast.Unot(self.operands_tags[X])
        X_and_not_Xt = vast.And(self.operands[X], not_Xt)
        Y_or_Yt = vast.Or(self.operands[Y], self.operands_tags[Y])
        minus2 = vast.Minus(X_and_not_Xt, Y_or_Yt)

        minus1_xor_minus2 = vast.Xor(minus1, minus2)
        Xt_or_Yt = vast.Or(self.operands_tags[X], self.operands_tags[Y])
        result = vast.Or(minus1_xor_minus2, Xt_or_Yt)
        return result

class TimesIFT(OperatorIFT):
    pass


class DivideIFT(OperatorIFT):
    pass


class ModIFT(OperatorIFT):
    pass


class PowerIFT(OperatorIFT):
    pass


# Logical
class LnotIFT(OperatorIFT):
    pass


class LandIFT(OperatorIFT):
    pass


class LorIFT(OperatorIFT):
    pass


# bitwise
class NotIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        Y = 0
        return self.operands_tags[Y]


class AndIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        # XXX: copy or not
        X = 0
        Y = 1
        Xt_and_Yt = vast.And(left=self.operands_tags[X], right=self.operands_tags[Y])
        Xt_and_Y = vast.And(left=self.operands_tags[X], right=self.operands[Y])
        Yt_and_X = vast.And(left=self.operands_tags[Y], right=self.operands[X])
        Yt_and_X_or_rev = vast.Or(left=Xt_and_Y, right=Yt_and_X)
        result = vast.Or(left=Xt_and_Yt, right=Yt_and_X_or_rev)
        return result


class OrIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        X = 0
        Y = 1
        not_X = vast.Unot(right=self.operands[X])
        not_Y = vast.Unot(right=self.operands[Y])
        Xt_and_Yt = vast.And(left=self.operands_tags[X], right=self.operands_tags[Y])
        Xt_and_not_Y = vast.And(left=self.operands_tags[X], right=not_Y)
        Yt_and_not_X = vast.And(left=self.operands_tags[Y], right=not_X)
        Yt_and_not_X_or_rev = vast.Or(left=Xt_and_not_Y, right=Yt_and_not_X)
        result = vast.Or(left=Xt_and_Yt, right=Yt_and_not_X_or_rev)
        return result


class XorIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        X = 0
        Y = 1
        return vast.Or(self.operands_tags[X], self.operands_tags[Y])


class XnorIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        X = 0
        Y = 1
        return vast.Or(self.operands_tags[X], self.operands_tags[Y])


# Relational
class LtIFT(OperatorIFT):
    pass


class GtIFT(OperatorIFT):
    pass


class GeIFT(OperatorIFT):
    pass


class LeIFT(OperatorIFT):
    pass


# Case Eq


class EqlIFT(OperatorIFT):
    pass


class NelIFT(OperatorIFT):
    pass


# Logical Eq
class EqIFT(OperatorIFT):
    pass


class NeIFT(OperatorIFT):
    pass


# Shift (impercise)
class LshiftaIFT(OperatorIFT):
    pass


class RshiftaIFT(OperatorIFT):
    pass


class LshiftIFT(OperatorIFT):
    pass


class RshiftIFT(OperatorIFT):
    pass


# ... cond, but let's forget that now.

rule_set = {
    # Reduction
    vast.Uand: UandIFT,
    vast.Unand: UnandIFT,
    vast.Uor: UorIFT,
    vast.Unor: UnorIFT,
    vast.Uxor: UxorIFT,
    vast.Uxnor: UxnorIFT,
    # Arithmetic
    vast.Uplus: UplusIFT,
    vast.Uminus: UminusIFT,
    vast.Plus: PlusIFT,
    vast.Minus: MinusIFT,
    vast.Times: TimesIFT,
    vast.Divide: DivideIFT,
    vast.Mod: ModIFT,
    vast.Power: PowerIFT,
    # Logical
    vast.Ulnot: LnotIFT,
    vast.Land: LandIFT,
    vast.Lor: LorIFT,
    # bitwise
    vast.Unot: NotIFT,
    vast.Uplus: UplusIFT,
    vast.Uminus: UminusIFT,
    vast.And: AndIFT,
    vast.Or: OrIFT,
    vast.Xor: XorIFT,
    vast.Xnor: XnorIFT,
    # Relational
    vast.LessThan: LtIFT,
    vast.GreaterThan: GtIFT,
    vast.GreaterEq: GeIFT,
    vast.LessEq: LeIFT,
    # Case Eq
    vast.Eql: EqlIFT,
    vast.NotEql: NelIFT,
    # Logical Eq
    vast.Eq: EqIFT,
    vast.NotEq: NeIFT,
    # Shift
    vast.Sla: LshiftaIFT,
    vast.Sra: RshiftaIFT,
    vast.Sll: LshiftIFT,
    vast.Sra: RshiftIFT,
}
