import tkinter as tk
from decimal import Decimal, InvalidOperation, getcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN
import re

getcontext().prec = 30

MIN_VAL = Decimal("-1000000000000000.00")
MAX_VAL = Decimal("1000000000000000.00")

number_pattern = re.compile(r"^-?\d+(?:[ ]\d{3})*(?:[.,]\d+)?$")

def normalize_number(value: str) -> Decimal:
    value = value.strip().replace(",", ".")
    if not number_pattern.match(value):
        raise ValueError("Некорректный ввод числа")
    try:
        num = Decimal(value.replace(" ", ""))
        if "E" in str(num).upper():
            raise InvalidOperation
        return num
    except InvalidOperation:
        raise ValueError("Некорректный ввод числа")

def format_result(value: Decimal) -> str:
    value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    int_part, _, frac_part = str(value).partition(".")
    int_part = f"{int(int_part):,}".replace(",", " ")
    if frac_part == "00":
        return int_part
    else:
        return f"{int_part}.{frac_part.rstrip('0')}"

def apply_operation(a: Decimal, b: Decimal, op: str) -> Decimal:
    if op == "+ Сложение":
        return (a + b)
    elif op == "- Вычитание":
        return (a - b)
    elif op == "* Умножение":
        return (a * b)
    elif op == "/ Деление":
        if b == 0:
            raise ZeroDivisionError
        return (a / b)
    else:
        raise ValueError("Неизвестная операция")

def calculate():
    try:
        num1_str = entry1.get()
        num2_str = entry2.get()
        num3_str = entry3.get()
        num4_str = entry4.get()

        num1 = normalize_number(num1_str)
        num2 = normalize_number(num2_str)
        num3 = normalize_number(num3_str)
        num4 = normalize_number(num4_str)

        op1 = operation_var1.get()
        op2 = operation_var2.get()
        op3 = operation_var3.get()

        mid = apply_operation(num2, num3, op2)

        high_ops = {"* Умножение", "/ Деление"}
        low_ops  = {"+ Сложение", "- Вычитание"}

        if op3 in high_ops and op1 in low_ops:
            right = apply_operation(mid, num4, op3)
            result = apply_operation(num1, right, op1)
        else:
            part = apply_operation(num1, mid, op1)
            result = apply_operation(part, num4, op3)

        if result < MIN_VAL or result > MAX_VAL:
            result_label.config(text="Переполнение диапазона!")
            return

        def format_fixed_decimals(val: Decimal, decimals: int) -> str:
            quant = Decimal("1").scaleb(-decimals)
            q = val.quantize(quant, rounding=ROUND_HALF_UP)
            s = str(q)
            int_part, _, frac_part = s.partition(".")
            int_grouped = f"{int(int_part):,}".replace(",", " ")
            return int_grouped if frac_part == "" else f"{int_grouped}.{frac_part}"

        formatted_result = format_fixed_decimals(result, decimals=6)

        rounding_method = rounding_var.get()
        if rounding_method == "Математическое":
            rounded_final = result.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        elif rounding_method == "Банковское":
            rounded_final = result.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
        elif rounding_method == "Усечение":
            rounded_final = result.quantize(Decimal("1"), rounding=ROUND_DOWN)
        else:
            rounded_final = result

        rounded_str = f"{int(rounded_final):,}".replace(",", " ")

        result_label.config(
            text=f"Результат: {formatted_result}\nОкруглённый итог: {rounded_str}"
        )

    except ZeroDivisionError:
        result_label.config(text="Ошибка: деление на 0!")
    except ValueError:
        result_label.config(text="Ошибка ввода!")



root = tk.Tk()
root.title("Калькулятор")
root.configure(bg="#fbe09e")

info_label = tk.Label(root, text="Кондратёнок Дарья Алексеевна\nКурс: 4\nГруппа: 4\nГод: 2025",
                      font=("Arial", 12), justify="left", bg="#fbe09e")
info_label.pack(pady=10)

def format_entry(event, entry: tk.Entry):
    value = entry.get().replace(" ", "").replace(",", ".")
    if value == "" or value == "-":
        return
    try:
        if "." in value:
            int_part, frac_part = value.split(".", 1)
            int_part = f"{int(int_part):,}".replace(",", " ")
            entry.delete(0, tk.END)
            entry.insert(0, f"{int_part}.{frac_part}")
        else:
            int_part = f"{int(value):,}".replace(",", " ")
            entry.delete(0, tk.END)
            entry.insert(0, int_part)
    except ValueError:
        pass

def bind_entry(entry: tk.Entry):
    entry.insert(0, "0")

    entry.bind("<KeyRelease>", lambda e: format_entry(e, entry))

    def paste_handler(e):
        if e.state & 0x4 and e.keycode == 86:
            entry.event_generate("<<Paste>>")
            return "break"

    entry.bind("<KeyPress>", paste_handler)

def release():
    # Очистка полей ввода
    entry1.delete(0, tk.END); entry1.insert(0, "0")
    entry2.delete(0, tk.END); entry2.insert(0, "0")
    entry3.delete(0, tk.END); entry3.insert(0, "0")
    entry4.delete(0, tk.END); entry4.insert(0, "0")

    # Сброс операций
    operation_var1.set("+ Сложение")
    operation_var2.set("+ Сложение")
    operation_var3.set("+ Сложение")

    # Сброс округления
    rounding_var.set("Математическое")

    # Очистка результата
    result_label.config(text="Результат: ")


entry1 = tk.Entry(root, width=30); bind_entry(entry1); entry1.pack(pady=5)
entry2 = tk.Entry(root, width=30); bind_entry(entry2); entry2.pack(pady=5)
entry3 = tk.Entry(root, width=30); bind_entry(entry3); entry3.pack(pady=5)
entry4 = tk.Entry(root, width=30); bind_entry(entry4); entry4.pack(pady=5)

operation_var1 = tk.StringVar(value="+ Сложение")
operation_var2 = tk.StringVar(value="+ Сложение")
operation_var3 = tk.StringVar(value="+ Сложение")

ops = ["+ Сложение", "- Вычитание", "* Умножение", "/ Деление"]

op_menu1 = tk.OptionMenu(root, operation_var1, *ops)
op_menu1.config(font=("Arial", 12), bg="#84452a", width=20, relief="raised")
op_menu1.pack(pady=5)

op_menu2 = tk.OptionMenu(root, operation_var2, *ops)
op_menu2.config(font=("Arial", 12), bg="#84452a", width=20, relief="raised")
op_menu2.pack(pady=5)

op_menu3 = tk.OptionMenu(root, operation_var3, *ops)
op_menu3.config(font=("Arial", 12), bg="#84452a", width=20, relief="raised")
op_menu3.pack(pady=5)

calc_button = tk.Button(root, text="Вычислить", command=calculate, font=("Arial", 12), bg="#84452a")
calc_button.pack(pady=5)

rounding_var = tk.StringVar(value="Математическое")
rounding_menu = tk.OptionMenu(root, rounding_var, "Математическое", "Банковское", "Усечение")
rounding_menu.config(font=("Arial", 12), bg="#84452a", width=20, relief="raised")
rounding_menu.pack(pady=10)

result_label = tk.Label(root, text="Результат: ", font=("Arial", 12), bg="#fbe09e")
result_label.pack(pady=10)

release_button = tk.Button(root, text="Сброс", command=release, font=("Arial", 12), bg="#84452a")
release_button.pack(pady=5)

root.mainloop()
