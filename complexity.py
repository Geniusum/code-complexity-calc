def calc_complexity(sourcecode:str):
    score: float = 0
    chars: dict = {
        "letters": {
            "list": [*"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"],
            "score_at_change": 0.09,
            "score_continue": 0.04
        },
        "numbers": {
            "list": [*"0123456789"],
            "score_at_change": 0.10,
            "score_continue": 0.05
        },
        "lang_syntax": {
            "list": [*"[]{{}}()-_\\/\"\'<>!?=~#&%*$^,;:§@|`°"],
            "score_at_change": 0.11,
            "score_continue": 0.07
        },
        "other": {
            "score_at_change": 0.06,
            "score_continue": 0.02
        }
    }
    last = "other"
    for char in [*sourcecode]:
        score_change = 0
        to_change = False
        if not char in chars[last]:
            to_change = True
        for chars_name, chars_dict in chars.items():
            try: chars_list = chars_dict["list"]
            except:
                if to_change:
                    last = chars_name
                    score_change = chars_dict["score_at_change"]
                else:
                    score_change = chars_dict["score_continue"]
            else:
                if char in chars_list:
                    if to_change:
                        last = chars_name
                        score_change = chars_dict["score_at_change"]
                    else:
                        score_change = chars_dict["score_continue"]
        score += score_change
    return round(score, 2)