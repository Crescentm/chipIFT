from pyverilog.vparser.parser import parse
import pyverilog.vparser.ast as vast
import os


class ASTVerilog:

    def __init__(
        self, file_list, include_list: list = [], define_list: list = []
    ) -> None:
        self.file_list: list = file_list
        self.ast: vast.Source = self.pasrser(file_list, include_list, define_list)

    def pasrser(
        self, file_list: list, include_list: list = [], define_list: list = []
    ) -> vast.Source | None:

        if len(file_list) == 0:
            return None

        for f in file_list:
            if not os.path.exists(f):
                raise IOError("file not found: " + f)

        ast, _ = parse(
            file_list,
            preprocess_include=include_list,
            preprocess_define=define_list,
            debug=False,
        )

        return ast

    def decls_add(self, delcs):
        modules = self.ast.children()[0].children()
        # for now, just one module
        module: vast.ModuleDef = modules[0]
        delc_list = module.items

        last_decl_index = 0
        for i, node in enumerate(delc_list):
            if isinstance(node, vast.Decl):
                last_decl_index = i

        print(last_decl_index)

    def gen_code(self):
        pass


def ast_pasrser_test():
    filelist = ["./tests/test.v"]
    ast = ASTVerilog(filelist)
    ast.decls_add(vast.Decl("reg", vast.Identifier("a")))


if __name__ == "__main__":
    ast_pasrser_test()
