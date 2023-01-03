import argparse
from typing import Mapping

import black
from markdown_it import MarkdownIt
from mdformat.renderer import RenderContext, RenderTreeNode
from mdformat.renderer.typing import Render
from mdformat.renderer._util import longest_consecutive_sequence


class ConfigurableBlack:

    CHANGES_AST = True

    @staticmethod
    def update_mdit(mdit: MarkdownIt) -> None:
        pass

    @staticmethod
    def add_cli_options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--line-length",
            type=int,
            default=88,
            metavar="",
            help="(black) How many characters per line to allow (default: 88)",
        )

    @staticmethod
    def format_python(unformatted: str, _info_str: str, context: RenderContext) -> str:
        line_length = (
            context.options["mdformat"]["line-length"]
            if "line-length" in context.options["mdformat"]
            else context.options["mdformat"]["line_length"]
        )
        return black.format_str(unformatted, mode=black.Mode(line_length=line_length))

    def _fence_postprocess(
        fence: str,
        node: RenderTreeNode,
        context: RenderContext,
    ) -> str:
        info_str = node.info.strip()
        lang = info_str.split(maxsplit=1)[0] if info_str else ""
        if lang == "python":
            code_block = node.content
            code_block = ConfigurableBlack.format_python(code_block, info_str, context)

            fence_char = "~" if "`" in info_str else "`"
            fence_len = max(3, longest_consecutive_sequence(code_block, fence_char) + 1)
            fence_str = fence_char * fence_len

            fence = f"{fence_str}{info_str}\n{code_block}{fence_str}"
        return fence

    RENDERERS: dict = {}

    POSTPROCESSORS: Mapping[str, Render] = {"fence": _fence_postprocess}
