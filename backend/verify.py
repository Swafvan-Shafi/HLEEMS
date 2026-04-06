import bcrypt
pw = b"password123"
hashed = b"$2b$12$R.S/mD9q8T.Y6/q7/d.UgeXqyA85E/27oAowA1N1wF7B1H5jX8nU."
print("Does it match?", bcrypt.checkpw(pw, hashed))
