# Punycode Codec in Python

This project helps you work with **Punycode** the way to convert international characters (like accents ) into ASCII text used in domain names.

## What the files do

- **char_unicode.py**  
  Explore letters and their variants. You can type a character like `a` and see all its accented versions, Unicode codes, and how they look in Punycode.

- **punycode.py**  
  Contains the code to convert between Unicode strings and Punycode. Use it to encode or decode domain names with international characters.

## Example of `char_unicode.py`

Run:

```bash
python char_unicode.py

Then type a letter, for example a. The script will show:

lua
Copy
Edit
Variants of 'a':

a -> a-- (U+0061)
á -> xn--1ca (U+00E1)
à -> xn--0ca (U+00E0)
â -> xn--2ca (U+00E2)
ã -> xn--3ca (U+00E3)
ä -> xn--4ca (U+00E4)
å -> xn--5ca (U+00E5)
ā -> xn--yda (U+0101)
You can try numbers or other letters as well.

Example of punycode.py
python
Copy
Edit
from punycode import encode, decode

# Encode Unicode string to Punycode
puny = encode('münich')
print(puny)  # Outputs something like: xn--mnich-kva

# Decode Punycode back to Unicode
unicode_str = decode(puny)
print(unicode_str)  # Outputs: münich
