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
        X = 0
        not_Xt = vast.Unot(self.operands_tags[X])
        X_and_not_Xt = vast.And(self.operands[X], not_Xt)
        neg1 = vast.Uminus(X_and_not_Xt)

        X_or_Xt = vast.Or(self.operands[X], self.operands_tags[X])
        neg2 = vast.Uminus(X_or_Xt)

        neg1_xor_neg2 = vast.Xor(neg1, neg2)
        result = vast.Or(neg1_xor_neg2, self.operands_tags[X])
        return result


class PlusIFT(OperatorIFT):
    def gen_rule(self) -> vast.Operator:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        not_Xt = vast.Unot(right=X_t)
        X_and_not_Xt = vast.And(left=X, right=not_Xt)

        not_Yt = vast.Unot(right=Y_t)
        Y_and_not_Yt = vast.And(left=Y, right=not_Yt)
        sum1 = vast.Plus(left=X_and_not_Xt, right=Y_and_not_Yt)

        X_or_Xt = vast.Or(left=X, right=X_t)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        sum2 = vast.Plus(left=X_or_Xt, right=Y_or_Yt)

        xor_result = vast.Xor(left=sum1, right=sum2)
        or_with_Xt = vast.Or(left=xor_result, right=X_t)

        result = vast.Or(left=or_with_Xt, right=Y_t)

        return result


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

    def gen_rule(self) -> vast.Node:
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        result = vast.Or(left=X_t, right=Y_t)
        return result


class DivideIFT(OperatorIFT):
    def gen_rule(self) -> vast.Node:
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        result = vast.Or(left=X_t, right=Y_t)
        return result


class ModIFT(OperatorIFT):
    pass


class PowerIFT(OperatorIFT):
    pass


# Logical
class LnotIFT(OperatorIFT):
    def gen_rule(self) -> vast.And:
        Y = self.operands[0]
        Y_t = self.operands_tags[0]
        not_Yt = vast.Unot(right=Y_t)
        Y_and_not_Yt = vast.And(left=Y, right=not_Yt)
        lnot_Y_and_not_Yt = vast.Ulnot(right=Y_and_not_Yt)
        uor_Yt = vast.Uor(right=Y_t)
        return vast.And(left=lnot_Y_and_not_Yt, right=uor_Yt)


class LandIFT(OperatorIFT):
    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        # (| (X & ~X_t))
        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        uor_X_and_unot_Xt = vast.Uor(right=X_and_unot_Xt)
        # (| (Y & ~Y_t))
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        uor_Y_and_unot_Yt = vast.Uor(right=Y_and_unot_Yt)
        # ( (| (X & ~X_t)) & (| (Y & ~Y_t)) )
        and_part = vast.And(left=uor_X_and_unot_Xt, right=uor_Y_and_unot_Yt)

        # (| (X | X_t))
        X_or_Xt = vast.Or(left=X, right=X_t)
        uor_X_or_Xt = vast.Uor(right=X_or_Xt)
        # (| (Y | Y_t))
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        uor_Y_or_Yt = vast.Uor(right=Y_or_Yt)
        # ( (| (X | X_t)) & (| (Y | Y_t)) )
        and_part2 = vast.And(left=uor_X_or_Xt, right=uor_Y_or_Yt)

        # O_t = ( (|(X & ~X_t)) & (|(Y & ~Y_t)) ) ^ ((|(X|X_t)) & (|(Y|Y_t)))
        result = vast.Xor(left=and_part, right=and_part2)

        return result


class LorIFT(OperatorIFT):
    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        # (| (X & ~X_t))
        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        uor_X_and_unot_Xt = vast.Uor(right=X_and_unot_Xt)
        # (| (Y & ~Y_t))
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        uor_Y_and_unot_Yt = vast.Uor(right=Y_and_unot_Yt)
        # ((| (X & ~X_t )) | (| (Y & ~Y_t)))
        left_or = vast.Or(left=uor_X_and_unot_Xt, right=uor_Y_and_unot_Yt)

        # (| (X | X_t))
        X_or_Xt = vast.Or(left=X, right=X_t)
        uor_X_or_Xt = vast.Uor(right=X_or_Xt)
        # (| (Y | Y_t))
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        uor_Y_or_Yt = vast.Uor(right=Y_or_Yt)
        # ((| (X | X_t)) | (| (Y | Y_t)))
        right_or = vast.Or(left=uor_X_or_Xt, right=uor_Y_or_Yt)

        # O_t = ((| (X & ~X_t )) | (| (Y & ~Y_t))) ^ ((| (X | X_t)) | (| (Y | Y_t)))
        result = vast.Xor(left=left_or, right=right_or)

        return result


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
    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        expr1 = vast.LessThan(
            left=X_and_unot_Xt, right=Y_or_Yt
        )  # ( ((X & ~X_t)) < (Y | Y_t) )

        X_or_Xt = vast.Or(left=X, right=X_t)
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        expr2 = vast.LessThan(
            left=X_or_Xt, right=Y_and_unot_Yt
        )  # ((X | X_t)) < (Y & ~Y_t)

        restult = vast.Xor(left=expr1, right=expr2)
        return restult


class GtIFT(OperatorIFT):

    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        expr1 = vast.GreaterThan(
            left=X_and_unot_Xt, right=Y_or_Yt
        )  # ( ((X & ~X_t)) > (Y | Y_t) )

        X_or_Xt = vast.Or(left=X, right=X_t)
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        expr2 = vast.GreaterThan(
            left=X_or_Xt, right=Y_and_unot_Yt
        )  # ((X | X_t)) > (Y & ~Y_t)

        result = vast.Xor(left=expr1, right=expr2)
        return result


class GeIFT(OperatorIFT):

    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        expr1 = vast.GreaterEq(
            left=X_and_unot_Xt, right=Y_or_Yt
        )  # ( ((X & ~X_t)) >= (Y | Y_t) )

        X_or_Xt = vast.Or(left=X, right=X_t)
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        expr2 = vast.GreaterEq(
            left=X_or_Xt, right=Y_and_unot_Yt
        )  # ((X | X_t)) >= (Y & ~Y_t)

        result = vast.Xor(left=expr1, right=expr2)
        return result


class LeIFT(OperatorIFT):

    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        expr1 = vast.LessEq(
            left=X_and_unot_Xt, right=Y_or_Yt
        )  # ( ( (X & ~X_t)) <= (Y | Y_t) )

        X_or_Xt = vast.Or(left=X, right=X_t)
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        expr2 = vast.LessEq(
            left=X_or_Xt, right=Y_and_unot_Yt
        )  # ((X | X_t)) <= (Y & ~Y_t)

        result = vast.Xor(left=expr1, right=expr2)

        return result


# Case Eq


class EqlIFT(OperatorIFT):
    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        # (X & ~X_t)
        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        # (Y | Y_t)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        # (X & ~X_t) === (Y | Y_t)
        expr1 = vast.Eql(left=X_and_unot_Xt, right=Y_or_Yt)

        # (X | X_t)
        X_or_Xt = vast.Or(left=X, right=X_t)
        # (Y & ~Y_t)
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        # (X | X_t) === (Y & ~Y_t)
        expr2 = vast.Eql(left=X_or_Xt, right=Y_and_unot_Yt)

        # O_t = expr1 ^ expr2
        result = vast.Xor(left=expr1, right=expr2)
        return result


class NelIFT(OperatorIFT):
    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        expr1 = vast.NotEq(
            left=X_and_unot_Xt, right=Y_or_Yt
        )  # ( (X & ~X_t) != (Y | Y_t) )

        X_or_Xt = vast.Or(left=X, right=X_t)
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        expr2 = vast.NotEq(
            left=X_or_Xt, right=Y_and_unot_Yt
        )  # ((X | X_t)) != (Y & ~Y_t)

        result = vast.Xor(left=expr1, right=expr2)
        return result


# Logical Eq
class EqIFT(OperatorIFT):

    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        # (X & ~X_t)
        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        # (Y | Y_t)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        # (X & ~X_t) === (Y | Y_t)
        expr1 = vast.Eql(left=X_and_unot_Xt, right=Y_or_Yt)

        # (X | X_t)
        X_or_Xt = vast.Or(left=X, right=X_t)
        # (Y & ~Y_t)
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        # (X | X_t) === (Y & ~Y_t)
        expr2 = vast.Eql(left=X_or_Xt, right=Y_and_unot_Yt)

        # O_t = expr1 ^ expr2
        result = vast.Xor(left=expr1, right=expr2)
        return result


class NeIFT(OperatorIFT):

    def gen_rule(self) -> vast.Xor:
        X = self.operands[0]
        Y = self.operands[1]
        X_t = self.operands_tags[0]
        Y_t = self.operands_tags[1]

        unot_Xt = vast.Unot(right=X_t)
        X_and_unot_Xt = vast.And(left=X, right=unot_Xt)
        Y_or_Yt = vast.Or(left=Y, right=Y_t)
        expr1 = vast.NotEq(
            left=X_and_unot_Xt, right=Y_or_Yt
        )  # ( (X & ~X_t) != (Y | Y_t) )

        X_or_Xt = vast.Or(left=X, right=X_t)
        unot_Yt = vast.Unot(right=Y_t)
        Y_and_unot_Yt = vast.And(left=Y, right=unot_Yt)
        expr2 = vast.NotEq(
            left=X_or_Xt, right=Y_and_unot_Yt
        )  # ((X | X_t)) != (Y & ~Y_t)

        result = vast.Xor(left=expr1, right=expr2)
        return result


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
