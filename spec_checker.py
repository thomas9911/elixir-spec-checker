def _is_spec(line):
    return line.startswith("@spec ") or line.startswith("@specp ")


def _is_function(line):
    return line.startswith("def ") or line.startswith("defp ")


def _filter_spec_or_def(lines):
    return [x for x in lines if _is_spec(x) or _is_function(x)]


def _remove_spec_prefix(line):
    return line.replace("@specp ", "", 1).replace("@spec ", "", 1)


def _remove_def_prefix(line):
    return line.replace("defp ", "", 1).replace("def ", "", 1)


def _remove_prefix(line):
    return _remove_def_prefix(_remove_spec_prefix(line))


def _get_function_name(line):
    return _remove_prefix(line).split("(")[0]


def _build_map(contents):
    spec = set([_get_function_name(x) for x in contents if _is_spec(x)])
    func = set([_get_function_name(x) for x in contents if _is_function(x)])
    return {"spec": spec, "function": func}


def _get_difference(map_specs):
    a = map_specs["spec"].difference(map_specs["function"])
    b = map_specs["function"].difference(map_specs["spec"])
    return {"spec": b, "function": a}


def _print_missing(map_difference, file=""):
    buffer = ""

    specs_error = _print_spec(map_difference["spec"], file)
    function_error = _print_func(map_difference["function"], file)

    if specs_error:
        buffer += specs_error
    if function_error:
        buffer += function_error

    if specs_error or function_error:
        return buffer


def _print_spec(specs, file):
    if len(specs) == 0:
        return False
    return "The specs are missing for functions in file {}: {}. \n".format(
        file, ", ".join(specs)
    )


def _print_func(funcs, file):
    if len(funcs) == 0:
        return False
    return "The functions are missing for specs in file {}: {}. \n".format(
        file, ", ".join(funcs)
    )


def check(contents, filename=""):
    contents = [x.strip() for x in contents.splitlines()]
    contents = _filter_spec_or_def(contents)
    k = _build_map(contents)
    diff = _get_difference(k)
    missing = _print_missing(diff, filename)
    if missing:
        print(missing)
        return False
    return True


def check_file(filename):
    with open(filename, "r") as f:
        contents = f.read()
    return check(contents, filename)


def print_help(argument):
    if argument in ["help", "-h", "--help"]:
        print(
            """Usage: python spec_checker.py PATH
        
Python script to check if your elixir functions have their specs specified.
Only checks the lib folder, also does not check the arity of the function. 
This script is just to check if you didn't forgot to add the spec to the function.

PATH:
    path to the root of your elixir project, defaults to '.' (dot)
        """
        )

        return True
    return False


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from glob import glob
    from fnmatch import fnmatch

    try:
        path = sys.argv[1]
    except IndexError:
        path = "."

    if not print_help(path):
        correct = []
        for item in Path(path).glob("lib/**/*"):
            if fnmatch(item, "*.exs") or fnmatch(item, "*.ex"):
                correct.append(check_file(item))

        if not all(correct):
            sys.exit(1)
