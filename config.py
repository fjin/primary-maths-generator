"""Shared configuration for the workbook generator."""

DEFAULT_TITLE = "Year 5 Mathematics Worksheet"
DEFAULT_QUESTIONS = 50
DEFAULT_COLUMNS = 2
DEFAULT_DIFFICULTY = "year5"
DEFAULT_SEED = 42

DIFFICULTY_LEVELS = {
    "year3": 1,
    "year4": 2,
    "year5": 3,
    "year6": 4,
    "naplan": 4,
    "selective": 5,
    "oc": 4,
    "icas": 5,
}

TOPIC_ALIASES = {
    "fraction": "fractions",
    "decimal": "decimals",
    "percent": "percentages",
    "percentage": "percentages",
    "word": "word_problems",
    "words": "word_problems",
}

