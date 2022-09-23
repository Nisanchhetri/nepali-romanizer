from rom_to_ne import NepaliConversion

while True:
    convert = NepaliConversion()
    sen = input("Enter sentence to romanize:")
    print("sentence length:", len(convert.convert_sentence(sen)),"\n")
    print(convert.convert_sentence(sen))
