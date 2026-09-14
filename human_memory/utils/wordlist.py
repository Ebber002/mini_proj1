"""
- recall.py     -> sample words (within or across categories) to build free
                    recall lists. Using several categories at once lets us
                    also look at semantic clustering during recall.
- capacity.py   -> draw words of increasing list length for serial recall /
                    span testing.
- chunking.py   -> build "meaningful" sequences from a single category
                    (e.g. 4 animals) versus "unstructured" sequences drawn
                    from mixed categories, to compare chunked vs unchunked
                    recall.
- secondary.py  -> reuse any list as a simple recall task while a secondary
                    task (articulatory suppression, finger tapping) is
                    performed concurrently.

Example:

    from utils.wordlist import WORDLIST, ALL_WORDS, CATEGORIES
    import random

    animals = WORDLIST["animals"]              # one category
    random_15 = random.sample(ALL_WORDS, 15)    # words pooled across all categories
"""

WORDLIST: dict[str, list[str]] = {
    "animals": [
        "dog", "cat", "horse", "lion", "tiger", "bear", "wolf", "deer",
        "rabbit", "mouse", "sheep", "goat", "pig", "cow", "fox",
        "elephant", "zebra", "monkey", "camel", "kangaroo",
    ],
    "birds": [
        "eagle", "sparrow", "robin", "owl", "hawk", "crow", "swan", "duck",
        "goose", "parrot", "penguin", "pigeon", "falcon", "heron", "stork",
        "finch", "magpie", "raven", "seagull", "woodpecker",
    ],
    "fruits": [
        "apple", "banana", "orange", "grape", "lemon", "peach", "pear",
        "plum", "cherry", "mango", "melon", "kiwi", "lime", "fig",
        "apricot", "coconut", "papaya", "guava", "blueberry", "raspberry",
    ],
    "vegetables": [
        "carrot", "potato", "onion", "garlic", "cabbage", "lettuce",
        "spinach", "broccoli", "pepper", "cucumber", "tomato", "pumpkin",
        "radish", "celery", "corn", "pea", "bean", "beet", "turnip",
        "zucchini",
    ],
    "furniture": [
        "chair", "table", "sofa", "bed", "desk", "shelf", "cabinet",
        "drawer", "bench", "stool", "wardrobe", "mirror", "lamp", "couch",
        "dresser", "rug", "curtain", "cushion", "mattress", "bookcase",
    ],
    "clothing": [
        "shirt", "pants", "dress", "jacket", "coat", "sweater", "scarf",
        "glove", "sock", "shoe", "boot", "hat", "belt", "skirt", "blouse",
        "vest", "tie", "jeans", "sandal", "mitten",
    ],
    "vehicles": [
        "car", "truck", "bus", "train", "plane", "boat", "ship", "bike",
        "scooter", "van", "taxi", "tractor", "subway", "ferry",
        "helicopter", "canoe", "wagon", "sled", "trolley", "motorcycle",
    ],
    "professions": [
        "doctor", "teacher", "lawyer", "farmer", "nurse", "chef", "pilot",
        "painter", "dentist", "plumber", "mechanic", "waiter", "librarian",
        "judge", "actor", "singer", "dancer", "soldier", "sailor", "baker",
    ],
    "body_parts": [
        "hand", "arm", "leg", "foot", "head", "eye", "ear", "nose",
        "mouth", "finger", "knee", "elbow", "shoulder", "neck", "chin",
        "cheek", "wrist", "ankle", "thumb", "hip",
    ],
    "weather": [
        "rain", "snow", "wind", "storm", "cloud", "fog", "sun", "thunder",
        "lightning", "hail", "breeze", "frost", "drizzle", "mist",
        "rainbow", "humidity", "sunshine", "blizzard", "drought", "tornado",
    ],
    "tools": [
        "hammer", "wrench", "screwdriver", "saw", "drill", "pliers",
        "nail", "screw", "ladder", "chisel", "file", "clamp", "level",
        "axe", "shovel", "rake", "ruler", "scissors", "tape", "wire",
    ],
    "musical_instruments": [
        "guitar", "piano", "violin", "drum", "flute", "trumpet", "cello",
        "harp", "saxophone", "clarinet", "trombone", "banjo", "tuba",
        "accordion", "xylophone", "oboe", "harmonica", "ukulele",
        "bagpipe", "cymbal",
    ],
    "sports": [
        "soccer", "tennis", "hockey", "golf", "boxing", "cricket", "rugby",
        "baseball", "basketball", "volleyball", "swimming", "running",
        "cycling", "skiing", "surfing", "wrestling", "archery", "fencing",
        "bowling", "rowing",
    ],
    "buildings": [
        "house", "school", "church", "castle", "tower", "hospital",
        "museum", "library", "bridge", "palace", "cottage", "barn",
        "cabin", "mansion", "skyscraper", "warehouse", "stadium", "temple",
        "lighthouse", "garage",
    ],
    "drinks": [
        "water", "coffee", "tea", "juice", "milk", "soda", "wine", "beer",
        "lemonade", "cocoa", "smoothie", "cider", "espresso", "latte",
        "cola", "punch", "nectar", "broth", "cordial", "mead",
    ],
}

# Convenience derivatives -- handy when an experiment doesn't care about
# category structure, only needs the raw pool or the list of category names.
CATEGORIES: list[str] = list(WORDLIST.keys())
ALL_WORDS: list[str] = [word for words in WORDLIST.values() for word in words]
