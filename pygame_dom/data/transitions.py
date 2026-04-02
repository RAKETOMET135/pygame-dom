import math
import pygame

def get_transition_value(t: float, speed: float, type: str) -> float:
    res_t: float = speed

    match type:
        case "ease":
            res_t = speed ** 2 * (3 - 2 * speed)
        case "ease-in":
            res_t = speed ** 2
        case "ease-out":
            res_t = 1 - (1 - speed) ** 2
        case "ease-in-out":
            res_t = 0.5 - 0.5 * math.cos(speed * math.pi)
    
    return res_t

def _transition_step(start_dict: dict, current_time: int, key: str, diff: float, value: list, old_value: float, max_value: float) -> float:
    if old_value == max_value:
        return old_value

    if not key in start_dict:
        start_dict[key] = [pygame.time.get_ticks(), old_value, max_value]
    else:
        if not start_dict[key][2] == max_value:
            start_dict[key] = [pygame.time.get_ticks(), old_value, max_value]

    if current_time - start_dict[key][0] >= value[0]:
        return max_value

    diff = start_dict[key][2] - start_dict[key][1]

    frame_step: float = diff * get_transition_value(0, min((1 / (value[0] / 1.5)) * (current_time - start_dict[key][0]), 1), value[1])

    return start_dict[key][1] + frame_step

def handle_transition(new_style: dict, old_style: dict, delay_dict: dict, time: int, start_dict: dict) -> None:
    transition: dict = new_style.get("transition", {})
    current_time: int = pygame.time.get_ticks()

    for key, item in new_style.items():

        # transition rule and for what is applied
        if (key in transition or "all" in transition):
            value: list = []

            if key in transition:
                value = transition[key]
            else:
                value = transition["all"]

            # transition delay
            if not key in delay_dict:
                delay_dict[key] = [0, new_style[key]]

                continue
            else:
                if not delay_dict[key][1] == new_style[key]:
                    del delay_dict[key]

                    continue

                if delay_dict[key][0] < value[2]:
                    delay_dict[key][0] += (current_time - time) / 1000

                    continue

            # transition
            if isinstance(item, int) or isinstance(item, float):
                diff: float = new_style[key] - old_style[key]

                old_style[key] = _transition_step(start_dict, current_time, key, diff, value, old_style[key], new_style[key])
            elif isinstance(item, str) and item.endswith("%"):
                old_style[key] = str(_transition_step(start_dict, current_time, key, 0, value, float(old_style[key][:len(old_style[key]) - 1]), float(new_style[key][:len(new_style[key]) - 1]))) + "%"
            elif isinstance(item, tuple) and (all(isinstance(x, int) for x in item) or all(isinstance(x, float)) for x in item):
                new_list: list = []

                for i in range(len(item)):
                    if i >= len(new_style[key]):
                        new_list.append(old_style[key][i])                        

                        continue

                    diff: float = new_style[key][i] - old_style[key][i]

                    new_list.append(_transition_step(start_dict, current_time, key + str(i), diff, value, old_style[key][i], new_style[key][i]))

                    if key in ["color", "background-color"]:
                        if new_list[i] > 255:
                            new_list[i] = 255
                        elif new_list[i] < 0:
                            new_list[i] = 0

                #print(new_list, new_style[key])

                old_style[key] = tuple(new_list)

            continue

        old_style[key] = item