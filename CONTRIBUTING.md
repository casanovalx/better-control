# Contribution

## Features

Feel free to propose PR and suggest new features, improvements. 

## Translations

If you wish to contribute with translation for the app into your language, please see the `utils/translations.py` file. if you have any doubts on it feel free to open a discussion or issue

step 1  : adding translations in `utils/translations.py`

step 2 : goto `src/better_control.py` and add your langauge as follows by editing this part

```
def load_language_and_translations(arg_parser, logger):
 
    settings = load_settings(logger)

    available_languages = ["en", "es", "pt", "fr", "id", "it", "tr"] --> add here


 
def process_language(arg_parser, logger):
 
    settings = load_settings(logger)

    available_languages = ["en", "es", "pt", "fr", "id", "it", "tr"] --> add here


```

step 3 : then in `src/ui/tabs/settings.py` edit this part
```
        lang_combo.append("pt", "Português")
        lang_combo.append("fr", "Français")
        lang_combo.append("id", "Bahasa Indonesia")
        lang_combo.append("it", "Italian")
        lang_combo.append("tr", "Turkish")
        lang_combo.append("add your new language here")

```
