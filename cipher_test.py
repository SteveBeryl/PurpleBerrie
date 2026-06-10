from cipher import caesar

cases = [
    ("test",  1, "uftu"),  # user's example was "uftv" but t+1=u, not v
    ("Test",  1, "Uftu"),
    ("hello", 3, "khoor"),
    ("abc XYZ", 1, "bcd YZA"),
    ("abc", -1, "zab"),
]

for text, shift, expected in cases:
    got = caesar(text, shift)
    status = "OK " if got == expected else "FAIL"
    print(f"{status}  caesar({text!r}, {shift}) = {got!r}  (expected {expected!r})")
