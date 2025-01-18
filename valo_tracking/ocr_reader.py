import easyocr

PROBABILITY_ACCEPTANCE = 0.7
reader = easyocr.Reader(['en'])

def read_image(provided_image):
    # print(reader.readtext(provided_image))
    result = reader.readtext(provided_image, allowlist='0123456789')
    for (bbox, text, prob) in result:
        print(f'Text: {text}, Probability: {prob}')
        if prob > PROBABILITY_ACCEPTANCE:
            return text
