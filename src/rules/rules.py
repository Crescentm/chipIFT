from pyverilog.ast_code_generator.codegen import Operator
import pyverilog.vparser.ast as vast


class OperatorIFT(object):
    def __init__(self,
                 operands: list = [],
                 operands_tags: list=[]
                 ) -> None:
        self.operands = operands
        self.operands_tags = operands_tags

    def gen_rule(self) -> vast.Operator:
        return vast.Operator(left=None, right=None)

class AndIFT(OperatorIFT):
    def __init__(self, operands: list, operands_tags: list) -> None:
        super().__init__(operands, operands_tags)
    
    def gen_rule(self) -> vast.Operator:
        # XXX: copy or not
        X = 0
        Y = 1
        Xt_and_Yt = vast.And(
                left = self.operands_tags[X],
                right = self.operands_tags[Y] 
                )
        Xt_and_Y = vast.And(
                left = self.operands_tags[X],
                right = self.operands[Y]
                )
        Yt_and_X = vast.And(
                left = self.operands_tags[Y],
                right = self.operands[X]
                )
        Yt_and_X_or_rev = vast.Or(
                left = Xt_and_Y,
                right = Yt_and_X
                )
        result = vast.Or(
                left = Xt_and_Yt,
                right = Yt_and_X_or_rev
                )
        return result


        pass



rule_set = {
        vast.And: AndIFT
        }
