import codecs

##################### Encoding #####################################

def split_chars(text):
    """Separate ASCII and extended characters."""
    ascii_bytes = bytearray()
    extended_chars = set()
    for ch in text:
        if ord(ch) < 128:
            ascii_bytes.append(ord(ch))
        else:
            extended_chars.add(ch)
    extended_chars = sorted(extended_chars)
    return bytes(ascii_bytes), extended_chars

def count_chars_below(text, limit):
    """Count characters with ordinal below the limit."""
    total = 0
    for ch in text:
        if ord(ch) < limit:
            total += 1
    return total

def find_next_occurrence(text, target_char, current_index, current_pos):
    """Find next occurrence of target_char, return updated (index, position)."""
    length = len(text)
    while True:
        current_pos += 1
        if current_pos == length:
            return (-1, -1)
        ch = text[current_pos]
        if ch == target_char:
            return current_index + 1, current_pos
        elif ch < target_char:
            current_index += 1

def encode_insertion(text, extended_chars):
    """Encode insertion positions and offsets."""
    previous_char = 0x80
    encoded_values = []
    last_index = -1
    for ch in extended_chars:
        index = pos = -1
        char_code = ord(ch)
        current_length = count_chars_below(text, char_code)
        delta = (current_length + 1) * (char_code - previous_char)
        while True:
            index, pos = find_next_occurrence(text, ch, index, pos)
            if index == -1:
                break
            delta += index - last_index
            encoded_values.append(delta - 1)
            last_index = index
            delta = 0
        previous_char = char_code

    return encoded_values

def threshold(j, bias):
    """Calculate threshold t for generalized integers."""
    res = 36 * (j + 1) - bias
    if res < 1:
        return 1
    if res > 26:
        return 26
    return res

alphabet = b"abcdefghijklmnopqrstuvwxyz0123456789"

def encode_generalized_int(num, bias):
    """Encode a number into a variable-length integer."""
    output = bytearray()
    j = 0
    while True:
        t = threshold(j, bias)
        if num < t:
            output.append(alphabet[num])
            return bytes(output)
        output.append(alphabet[t + ((num - t) % (36 - t))])
        num = (num - t) // (36 - t)
        j += 1

def adjust_bias(delta, is_first, total_chars):
    """Bias adjustment for encoding."""
    if is_first:
        delta //= 700
    else:
        delta //= 2
    delta += delta // total_chars

    adjustments = 0
    while delta > 455:
        delta //= 35
        adjustments += 36
    bias = adjustments + (36 * delta // (delta + 38))
    return bias

def encode_deltas(base_length, deltas):
    """Encode delta values with bias adaptation."""
    output = bytearray()
    bias = 72
    for i, delta in enumerate(deltas):
        encoded_num = encode_generalized_int(delta, bias)
        output.extend(encoded_num)
        bias = adjust_bias(delta, i == 0, base_length + i + 1)
    return bytes(output)

def encode_text(text):
    """Convert text into punycode bytes."""
    ascii_part, extended_part = split_chars(text)
    deltas = encode_insertion(text, extended_part)
    encoded_ext = encode_deltas(len(ascii_part), deltas)
    if ascii_part:
        return ascii_part + b"-" + encoded_ext
    return encoded_ext

##################### Decoding #####################################

def decode_generalized_int(encoded, position, bias, errors):
    """Decode a variable-length integer from bytes."""
    result = 0
    weight = 1
    j = 0
    while True:
        try:
            val = encoded[position]
        except IndexError:
            if errors == "strict":
                raise UnicodeDecodeError("punycode", encoded, position, position + 1,
                                         "Incomplete punycode data")
            return position + 1, None
        position += 1
        if 0x41 <= val <= 0x5A:
            digit = val - 0x41
        elif 0x30 <= val <= 0x39:
            digit = val - 22
        elif errors == "strict":
            raise UnicodeDecodeError("punycode", encoded, position - 1, position,
                                     f"Invalid character {encoded[position - 1]!r}")
        else:
            return position, None
        t = threshold(j, bias)
        result += digit * weight
        if digit < t:
            return position, result
        weight *= (36 - t)
        j += 1

def decode_insertion(ascii_text, encoded_ext, errors):
    """Rebuild original text by inserting decoded chars."""
    char_code = 0x80
    pos = -1
    bias = 72
    ext_pos = 0

    while ext_pos < len(encoded_ext):
        new_pos, delta = decode_generalized_int(encoded_ext, ext_pos, bias, errors)
        if delta is None:
            return ascii_text  # Stop decoding on error, return what we have
        pos += delta + 1
        char_code += pos // (len(ascii_text) + 1)
        if char_code > 0x10FFFF:
            if errors == "strict":
                raise UnicodeDecodeError("punycode", encoded_ext, pos - 1, pos,
                                         f"Invalid Unicode codepoint U+{char_code:x}")
            char_code = ord("?")
        pos %= (len(ascii_text) + 1)
        ascii_text = ascii_text[:pos] + chr(char_code) + ascii_text[pos:]
        bias = adjust_bias(delta, ext_pos == 0, len(ascii_text))
        ext_pos = new_pos
    return ascii_text

def decode_text(encoded_text, errors):
    """Decode punycode bytes to unicode text."""
    if isinstance(encoded_text, str):
        encoded_text = encoded_text.encode("ascii")
    if isinstance(encoded_text, memoryview):
        encoded_text = bytes(encoded_text)
    split_pos = encoded_text.rfind(b"-")
    if split_pos == -1:
        ascii_part = ""
        ext_part = encoded_text.upper()
    else:
        try:
            ascii_part = str(encoded_text[:split_pos], "ascii", errors)
        except UnicodeDecodeError as exc:
            raise UnicodeDecodeError("ascii", encoded_text, exc.start, exc.end,
                                     exc.reason) from None
        ext_part = encoded_text[split_pos + 1:].upper()
    try:
        return decode_insertion(ascii_part, ext_part, errors)
    except UnicodeDecodeError as exc:
        offset = split_pos + 1
        raise UnicodeDecodeError("punycode", encoded_text,
                                 offset + exc.start, offset + exc.end,
                                 exc.reason) from None

### Codec classes and registration

class PunycodeCodec(codecs.Codec):

    def encode(self, input_text, errors='strict'):
        encoded = encode_text(input_text)
        return encoded, len(input_text)

    def decode(self, input_bytes, errors='strict'):
        if errors not in ('strict', 'replace', 'ignore'):
            raise UnicodeError(f"Unsupported error mode: {errors}")
        decoded = decode_text(input_bytes, errors)
        return decoded, len(decoded)

class PunycodeIncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input_text, final=False):
        return encode_text(input_text)

class PunycodeIncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input_bytes, final=False):
        if self.errors not in ('strict', 'replace', 'ignore'):
            raise UnicodeError(f"Unsupported error mode: {self.errors}")
        return decode_text(input_bytes, self.errors)

class PunycodeStreamWriter(PunycodeCodec, codecs.StreamWriter):
    pass

class PunycodeStreamReader(PunycodeCodec, codecs.StreamReader):
    pass

def getregentry():
    return codecs.CodecInfo(
        name='punycode',
        encode=PunycodeCodec().encode,
        decode=PunycodeCodec().decode,
        incrementalencoder=PunycodeIncrementalEncoder,
        incrementaldecoder=PunycodeIncrementalDecoder,
        streamwriter=PunycodeStreamWriter,
        streamreader=PunycodeStreamReader,
    )
