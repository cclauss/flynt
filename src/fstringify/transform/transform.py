import astor
import ast
from fstringify.transform.node_transformer import fstringify_node
from fstringify.format import force_double_quote_fstring, set_quote_type
import copy
from typing import Dict, Tuple

def fstringify_code(code: str, quote_type: str = None) -> Tuple[str, Dict]:
    """Convert a block of with a %-formatted string to an f-string

    Args:
        code (str): The code to convert.


    Returns:
       The code formatted with f-strings if possible else it's left unchanged.
    """

    from fstringify.utils import get_indent

    converted = None
    meta = dict(changed=False, lineno=1, col_offset=-22, skip=True)

    code_strip = code.strip()

    if code_strip == "" or code_strip.startswith("#"):
        meta["skip"] = True
        return code, meta

    try:
        tree = ast.parse(code_strip)
        # if debug:
        #     pp_ast(tree)
        converted, meta = fstringify_node(copy.deepcopy(tree))
    except SyntaxError as e:
        meta["skip"] = code.rstrip().endswith(
            ":"
        ) or "cannot include a blackslash" in str(e)
    except Exception as e2:
        meta["skip"] = False

    if meta["changed"] and converted:
        new_code = astor.to_source(converted)
        indent = get_indent(code)
        new_code = indent + new_code.strip()
        if quote_type is None:
            new_code = force_double_quote_fstring(new_code)
        else:
            new_code = set_quote_type(new_code, quote_type)
        new_code = new_code.replace('\n', '')
        return new_code, meta

    return code, meta
