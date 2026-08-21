import random
import utils.gpg
import utils.points
import sympy as sp
from logger import log

x = sp.Symbol('x')

def char_to_ascii(char):
    return ord(char)

def generate_secret_key(length):
    return [round(random.uniform(0, 100), 2) for _ in range(length)]

def generate_base_salt_equation(secret_key):
    if not secret_key:
        return sp.Integer(0)

    base_salt_equation = sp.Integer(1)
    for key in secret_key:
        base_salt_equation *= (x - key)

    return sp.expand(base_salt_equation)

def encryptMessage(message, gpg_key_path, salt_equation_type):
    try:
        ascii_values = [char_to_ascii(char) for char in message]
        total_chars = len(ascii_values)
        secret_key = generate_secret_key(total_chars)

        gpg_key = utils.gpg.read_gpg_file(gpg_key_path)

        if gpg_key is not None:
            encrypted_data = utils.gpg.encrypt_secret_key(secret_key, gpg_key)
            points = utils.points.generate_points(secret_key, ascii_values)

            base_polynomial = sp.interpolate(points, x)
            integral = sp.integrate(base_polynomial, x)
            calculus_wrapper = sp.Derivative(integral, x)

            base_salt_equation = generate_base_salt_equation(secret_key)
            if salt_equation_type == "Sine":
                salt_equation = sp.sin(base_salt_equation)
            elif salt_equation_type == "Cosine":
                salt_equation = sp.cos(base_salt_equation) - 1
            elif salt_equation_type == "Tan":
                salt_equation = sp.tan(base_salt_equation)
            elif salt_equation_type == "Square Root":
                salt_equation = sp.sqrt(base_salt_equation)
            elif salt_equation_type == "Log":
                salt_equation = sp.log(base_salt_equation + 1)
            else:
                salt_equation = base_salt_equation

            sym_expression = salt_equation + calculus_wrapper
            latex_repr = sp.latex(sym_expression)

            log("Encryption process completed successfully.", "encryption_logger", text_color="#677D6A")

            payload = {
                "encrypted_data": encrypted_data,
                "equation": str(sym_expression),
                "latex": latex_repr,
                "sympy_expr": sym_expression
            }

            return payload
    except Exception as e:
        log(f"Error during encryption: {str(e)}", "encryption_logger", text_color="#f54842")
        return None
