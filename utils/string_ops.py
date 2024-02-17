import string


def clean_text(text):
    """
    Normalize text by converting to lowercase, removing punctuation, and removing extra spaces
    :param text:
    :return:
    """
    # Convert to lowercase
    lowercased = text.lower()
    # Remove punctuation
    no_punctuation = lowercased.translate(str.maketrans('', '', string.punctuation))
    # Remove extra spaces and replace internal multiple spaces with single space
    normalized = ' '.join(no_punctuation.split())
    return normalized
