import sys, os, argparse

PROG = "Markdown Title Number Generator by Yongj.Zhuang"
DESC = "Parse and Generate Makdown Title Numbers"

def parse_args(args: list[str]) -> argparse.Namespace:
    ap: argparse.ArgumentParser = argparse.ArgumentParser(prog=PROG, description=DESC, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("-f", "--file", type=str, help="markdown file path", default="")
    ap.add_argument("--dryrun", help="dry run, i.e., output the content only", action="store_true")
    return ap.parse_args(args)


def load_lines(file: str) -> list[str]:
    with open(file) as f: return [l[0:len(l)-1] if l[len(l)-1] == "\n" else l for l in f.readlines()]


def store_lines(lines: list[str], file: str):
    with open(file, mode="w") as f:
        c = "\n".join(lines)
        f.write(c)


def process_line(curr_level: int, ctx: dict[int], line: str, in_code_block: bool) -> tuple[int, dict[int], str, bool]:
    if line.startswith("```"): return curr_level, ctx, line, not in_code_block
    if in_code_block: return curr_level, ctx, line, in_code_block # ignore these lines
    if line.startswith("<!--"): return curr_level, ctx, line, in_code_block # line is commented

    # check if the line is a title line
    levels: int = 0
    end: int = 1
    for i in range(len(line)):
        s = line[i]
        if levels > 0 and s != "#": # special case like: "## my title #", we consider this as a level two title
            end = i
            break
        if s == " ": continue # leading space characters
        if s != " " and s != "#": # illegal characters
            end = i
            break
        if s == "#": levels += 1

    if levels < 1: return curr_level, ctx, line, False # not a title

    if levels < curr_level: # e.g., from "### ... "  to "## ...", reset some of the numbers
        for k in ctx.keys():
            if k > levels: ctx[k] = 0

    if levels not in ctx: ctx[levels] = 1
    else: ctx[levels] = ctx[levels] + 1

    next = ""
    for i in range(levels):
        if i > 0: next = next + "." + str(ctx[i + 1])
        else: next = str(ctx[i + 1])

    j = end
    k = end

    isnum = False
    while k < len(line):
        if line[k].isnumeric():
            isnum = True
            if k < len(line)-1: k = k + 1
            continue
        if line[k] == " " or (line[k] == "." and isnum):
            if k < len(line)-1: k = k + 1
            continue
        break

    if line[k] == " ": line = line[0:j] + " " + next + line[k:]
    else: line = line[0:j] + " " + next + " " + line[k:]

    return levels, ctx, line, False


def number_titles(lines: list[str]) -> list[str]:
    ctx = {}
    cl = 1
    pline = []
    in_code_block = False

    for l in lines:
        cl, ctx, l, in_code_block = process_line(cl, ctx, l, in_code_block)
        pline.append(l)
    return pline

def print_lines(lines: list[str]):
    for i in range(len(lines)): print(lines[i])


def main():
    args = parse_args(sys.argv[1:])
    if not args.file: return

    ll = load_lines(args.file)
    nt = number_titles(ll)
    if args.dryrun:
        print_lines(nt)
        return
    store_lines(nt, args.file)

if __name__ == "__main__":
    main()

