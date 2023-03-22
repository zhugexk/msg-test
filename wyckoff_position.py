import pprint

import sympy
import numpy as np
import json
import re
import pprint


def cal_operator_from_coordinate(x, y, z, coor):
    res = [0, 0, 0]
    for i, c in enumerate([x, y, z]):
        find = re.findall(r"(-?)([0-9]?)"+c, coor)
        if not find:
            continue
        find = find[0]
        coeff = int(find[1]) if find[1] != "" else 1
        coeff = coeff if not find[0] else -coeff
        res[i] = coeff
    return res


def cal_msg_operator_from_spin(spin):
    res = []
    for s in spin:
        res.append(cal_operator_from_coordinate("mx", "my", "mz", s))
    return res


def cal_space_operator_and_translation_from_coordinates(coors):
    space_operator, translation = [], []
    for coor in coors:
        space_operator.append(cal_operator_from_coordinate("x", "y", "z", coor))
        translation.append(cal_translation_from_coordinate(coor))
    return space_operator, translation


def cal_translation_from_coordinate(coor):
    divider = re.findall(r"([1-9]*)/([1-9]*)", coor)
    if divider:
        return sympy.Rational(int(divider[0][0]), int(divider[0][1]))
    else:
        return 0


def cal_msg():
    with open("data/wyckoff_position.json", "r") as f:
        wyckoff_position_list = json.load(f)
    res = []
    for wp in wyckoff_position_list:
        group = {"id": wp["id"], "translation": [], "translation_": [], "operations": []}
        for translation in wp["translation"]:
            if not re.findall(r"'", translation):
                coors = re.split(r",", translation[1:-1])
                group["translation"].append([cal_translation_from_coordinate(coor) for coor in coors])
            else:
                coors = re.split(r",", translation[1:-2])
                group["translation_"].append([cal_translation_from_coordinate(coor) for coor in coors])
        general_positions = wp["wyckoff_positions"][0]["positions"]
        for position in general_positions:
            coors = re.split(r"\|", position)[0][1:-1]
            spin = re.split(r"\|", position)[1][1:-1]
            coors = re.split(r",", coors)
            spin = re.split(r",", spin)
            space_operator, translation = cal_space_operator_and_translation_from_coordinates(coors)
            msg_operator = cal_msg_operator_from_spin(spin)
            group["operations"].append({
                "space_operator": space_operator,
                "translation": translation,
                "msg_operator": msg_operator
            })
        res.append(group)
    return res


if __name__ == "__main__":
    msg = cal_msg()
    with open("data/msg.py", "w") as f:
        f.write(pprint.pformat(msg))



