module.exports = {
    "parserOptions": {
        "ecmaVersion": 6,
    },
    "env": {
        "browser": true,
    },
    "extends": "eslint:recommended",
    "globals": {
        "$": "readonly",
        "$$": "readonly",
        "django": "readonly",
        "FullCalendar": "readonly",
        "Datepicker": "readonly"
    }
};
