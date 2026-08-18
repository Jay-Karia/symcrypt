import random
import utils.gpg
import utils.points
import sympy as sp
from logger import log

x = sp.Symbol('x')

def char_to_ascii(char):
  ascii_value = ord(char)
  return ascii_value

def generate_secret_key(length):
  secret_key = [round(random.uniform(0, 100), 2) for _ in range(length)]
  return secret_key

def generate_base_salt_equation(secret_key):
  if not secret_key:
    return sp.Integer(0)

  base_salt_equation = sp.Integer(1)
  for key in secret_key:
    base_salt_equation *= (x - key)

  return sp.expand(base_salt_equation)

def encryptMessage(message, gpg_key_path, salt_equation_type):
  try:
    # Convert all the characters to ascii
    ascii_values = [char_to_ascii(char) for char in message]

    # Get total number of characters in the message
    total_chars = len(ascii_values)

    # Generate a secret key
    secret_key = generate_secret_key(total_chars)

    # Read the GPG key file
    gpg_key = utils.gpg.read_gpg_file(gpg_key_path)

    # Encrypt the secret key using the GPG key
    if gpg_key is not None:
      encrypted_data = utils.gpg.encrypt_secret_key(secret_key, gpg_key)

      # Generate geometric points
      points = utils.points.generate_points(secret_key, ascii_values)

      # Generate equation
      base_polynomial = sp.interpolate(points, x)
      integral = sp.integrate(base_polynomial, x)
      calculus_wrapper = sp.Derivative(integral, x)

      # Generate salt equation based on user selection
      base_salt_equation = generate_base_salt_equation(secret_key)
      if (salt_equation_type == "Sine"):
        salt_equation = sp.sin(base_salt_equation)
      elif (salt_equation_type == "Cosine"):
        salt_equation = sp.cos(base_salt_equation) - 1
      elif (salt_equation_type == "Tan"):
        salt_equation = sp.tan(base_salt_equation)
      elif (salt_equation_type == "Square Root"):
        salt_equation = sp.sqrt(base_salt_equation)
      elif (salt_equation_type == "Log"):
        salt_equation = sp.log(base_salt_equation + 1)
      else:
        salt_equation = base_salt_equation

      final_equation = salt_equation + calculus_wrapper
      final_equation = sp.pretty(final_equation, use_unicode=True)
      print(final_equation)
      log("Encryption process completed successfully.", "encryption_logger", text_color="#4CAF50")

      log(final_equation, "math_equation_logger", text_color="#4CAF50")

      payload = {
          "encrypted_data": encrypted_data,
          "equation": str(final_equation)
      }

      return payload
  except Exception as e:
    log(f"Error during encryption: {str(e)}", "encryption_logger", text_color="#f54842")
