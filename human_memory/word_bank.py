# Words organized by category so main.py (and experiments/recall.py) can
# sample one word per category per list, reducing semantic clustering
# within each 15-word sequence used in the Free Recall block.

WORD_CATEGORIES = {
    "animals": [
        "dog", "cat", "cow", "pig", "horse", "sheep", "goat", "duck", "hen",
        "fox", "wolf", "bear", "deer", "mouse", "rat", "frog", "bird", "fish",
        "bee", "ant", "owl", "bat", "seal", "crab",
    ],
    "furniture": [
        "chair", "table", "bed", "desk", "sofa", "couch", "shelf", "stool",
        "bench", "drawer", "mirror", "lamp", "rug", "closet", "dresser",
        "cushion", "stand", "crib", "trunk", "rack",
    ],
    "vehicles": [
        "car", "bus", "van", "truck", "bike", "train", "boat", "ship",
        "plane", "jeep", "cart", "sled", "canoe", "scooter", "taxi", "tram",
        "ferry", "wagon", "buggy", "rocket",
    ],
    "fruit": [
        "apple", "pear", "plum", "grape", "lemon", "lime", "peach", "mango",
        "melon", "cherry", "berry", "fig", "kiwi", "date", "guava", "papaya",
        "orange", "apricot", "coconut", "banana",
    ],
    "clothing": [
        "shirt", "coat", "hat", "cap", "sock", "shoe", "boot", "belt",
        "glove", "scarf", "dress", "skirt", "jacket", "sweater", "vest",
        "tie", "robe", "sandal", "blazer", "mitten",
    ],
    "tools": [
        "hammer", "wrench", "drill", "saw", "nail", "screw", "ladder", "axe",
        "mallet", "chisel", "file", "clamp", "level", "brush", "shovel",
        "rake", "hose", "wire", "bolt", "knife",
    ],
    "body_parts": [
        "head", "arm", "leg", "hand", "foot", "eye", "ear", "nose", "mouth",
        "chin", "neck", "back", "chest", "knee", "elbow", "wrist", "ankle",
        "thumb", "finger", "hip",
    ],
    "occupations": [
        "doctor", "nurse", "teacher", "farmer", "baker", "cook", "chef",
        "pilot", "driver", "judge", "lawyer", "dentist", "barber", "plumber",
        "painter", "waiter", "singer", "actor", "coach", "clerk",
    ],
    "vegetables": [
        "carrot", "potato", "onion", "garlic", "pepper", "corn", "pea",
        "bean", "celery", "radish", "cabbage", "lettuce", "spinach",
        "turnip", "beet", "squash", "pumpkin", "broccoli", "cucumber",
        "kale",
    ],
    "kitchenware": [
        "pot", "pan", "cup", "mug", "plate", "bowl", "spoon", "fork", "tray",
        "jar", "pitcher", "kettle", "toaster", "blender", "ladle", "whisk",
        "strainer", "napkin", "apron", "grater",
    ],
}
