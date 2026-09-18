import re


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_valid_cpf(cpf: str) -> bool:
    cpf = only_digits(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def digit(cpf_partial: str) -> int:
        total = sum(int(d) * w for d, w in zip(cpf_partial, range(len(cpf_partial) + 1, 1, -1)))
        result = (total * 10) % 11
        return 0 if result == 10 else result

    return digit(cpf[:9]) == int(cpf[9]) and digit(cpf[:10]) == int(cpf[10])


def mask_cpf(cpf: str) -> str:
    cpf = only_digits(cpf)
    if len(cpf) != 11:
        return cpf
    return f"***.***.{cpf[6:9]}-{cpf[9:]}"


def format_cpf(cpf: str) -> str:
    cpf = only_digits(cpf)
    if len(cpf) != 11:
        return cpf
    return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
