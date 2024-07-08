import complexity as c

file_path: str = "sample.py"
file_content: str = open(file_path).read()

print(c.calc_complexity(file_content))