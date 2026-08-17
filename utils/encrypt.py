import random
import utils.gpg
import utils.points
import sympy as sp

x = sp.Symbol('x')

def char_to_ascii(char):
  ascii_value = ord(char)
  return ascii_value

def generate_secret_key(length):
  secret_key = [round(random.uniform(0, 100), 2) for _ in range(length)]
  return secret_key

def encryptMessage(message, gpg_key_path):
  # Get all the characters (including new lines) from the message
  message_bytes = message.encode('utf-8')

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
    print(f"Encrypted Data: {encrypted_data}")

  # Generate geometric points
  points = utils.points.generate_points(secret_key, ascii_values)

  # Generate equation
  base_polynomial = sp.interpolate(points, x)
  integral = sp.integrate(base_polynomial, x)
  calculus_wrapper = sp.Derivative(integral, x)

  print(calculus_wrapper)
