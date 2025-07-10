#!/usr/bin/env python3
import codecs

# Define similar-looking or related Unicode variants for base letters
unicode_groups = {
    'a': ['a', 'á', 'à', 'â', 'ã', 'ä', 'å', 'ā'],
    'c': ['c', 'ç', 'ć', 'č'],
    'd': ['d', 'ď', 'đ'],
    'e': ['e', 'é', 'è', 'ê', 'ë', 'ē', 'ė', 'ę'],
    'g': ['g', 'ğ', 'ģ'],
    'h': ['h', 'ĥ', 'ħ'],
    'i': ['i', 'í', 'ì', 'î', 'ï', 'ī', 'į', 'ı'],
    'j': ['j', 'ĵ'],
    'k': ['k', 'ķ'],
    'l': ['l', 'ĺ', 'ľ', 'ļ', 'ł'],
    'n': ['n', 'ñ', 'ń', 'ň', 'ņ'],
    'o': ['o', 'ó', 'ò', 'ô', 'õ', 'ö', 'ø', 'ō', 'œ'],
    'r': ['r', 'ŕ', 'ř', 'ŗ'],
    's': ['s', 'ś', 'š', 'ş', 'ș'],
    't': ['t', 'ť', 'ţ', 'ț'],
    'u': ['u', 'ú', 'ù', 'û', 'ü', 'ū', 'ų'],
    'w': ['w', 'ŵ'],
    'y': ['y', 'ý', 'ÿ', 'ŷ'],
    'z': ['z', 'ź', 'ž', 'ż'],
}

def punycode_encode(char: str) -> str:
    """
    Encodes a single Unicode character into its Punycode representation.
    Returns ASCII characters with a trailing dash ('-') and non-ASCII as 'xn--<code>'.
    """
    try:
        encoded = codecs.encode(char, 'punycode').decode('ascii')
        return f"xn--{encoded}" if ord(char) > 127 else f"{encoded}-"
    except Exception as e:
        return f"[error: {e}]"

def main():
    print("Unicode & Punycode Character Viewer\n")
    
    while True:
        user_input = input("Enter a character (or 'exit' to quit): ").strip()

        if user_input.lower() == 'exit':
            print("Bye!")
            break

        if len(user_input) != 1:
            print("❌ Please enter exactly one character.\n")
            continue

        if user_input in unicode_groups:
            print(f"\nVariants of '{user_input}':\n")
            for ch in unicode_groups[user_input]:
                puny = punycode_encode(ch)
                print(f"{ch} -> {puny} (U+{ord(ch):04X})")
            print()
        else:
            # Print Punycode and Unicode for any single char (number, symbol, etc.)
            puny = punycode_encode(user_input)
            print(f"\n{user_input} -> {puny} (U+{ord(user_input):04X})\n")

if __name__ == "__main__":
    main()
