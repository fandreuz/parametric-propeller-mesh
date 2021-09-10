brackets_dict = dict()
brackets_dict["("] = ")"
brackets_dict["["] = "]"
brackets_dict["{"] = "}"


def find_balanced(bigstring, sub, bracket="("):
    try:
        idx = bigstring.index(sub)
    except ValueError:
        return None

    counter = 0
    first_bracket_idx = -1
    for i, c in enumerate(bigstring[idx + len(sub) :]):
        if c == bracket:
            counter += 1
            if first_bracket_idx == -1:
                first_bracket_idx = i
        elif c == brackets_dict[bracket]:
            counter -= 1
            if counter == 0:
                tentative_bounds = (
                    idx + len(sub) + first_bracket_idx + 1,
                    idx + len(sub) + i,
                )
                # we want to preserve trailing and leading spaces
                tentative_string = bigstring[
                    tentative_bounds[0] : tentative_bounds[1]
                ]
                n_of_left_blank = len(tentative_string) - len(
                    tentative_string.lstrip()
                )
                n_of_right_blank = len(tentative_string) - len(
                    tentative_string.rstrip()
                )

                return (
                    tentative_bounds[0] + n_of_left_blank,
                    tentative_bounds[1] - n_of_right_blank,
                )
    raise ValueError(
        "The string is not balanced:\n{}\n\n{} - {}".format(
            bigstring, sub, bracket
        )
    )
