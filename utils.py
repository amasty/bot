import settings
from commands import _system


def get_commands_list():
    """ Список комманд бота

    Returns:
        str: список комманд бота
    """
    text = ''
    for c in _system.commands:
        if c.name in settings.commands_black_list:
            continue

        text += '{}: {}\n'.format(c.keys[0], c.description)

    return text


def calc_damerau_levenshtein_distance(one, another):
    """ Расстояние Дамерау — Левенштейна

    Args:
        one (str): строка для нахождения расстояния
        another (str): строка для нахождения расстояния

    Returns:
        float: расстояние между строками
    """
    d = {}
    len_one = len(one)
    len_another = len(another)

    for i in range(-1, len_one + 1):
        d[(i, -1)] = i + 1

    for j in range(-1, len_another + 1):
        d[(-1, j)] = j + 1

    for i in range(len_one):
        for j in range(len_another):
            if one[i] == another[j]:
                cost = 0
            else:
                cost = 1

            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )

            if i and j and one[i] == another[j - 1] and one[i - 1] == another[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition

    return d[len_one - 1, len_another - 1]
