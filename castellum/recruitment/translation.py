from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import translator

from .models.attributesets import AttributeChoice
from .models.attributesets import AttributeDescription


class AttributeDescriptionTranslationsOptions(TranslationOptions):
    fields = ('label', '_filter_label',)


class AttributeChoiceTranslationsOptions(TranslationOptions):
    fields = ('label',)


translator.register(AttributeDescription, AttributeDescriptionTranslationsOptions)
translator.register(AttributeChoice, AttributeChoiceTranslationsOptions)
