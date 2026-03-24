"""Tests for the internationalization module."""
from __future__ import annotations
from unittest import mock

from src.i18n import t, set_language, get_language, detect_language, TRANSLATIONS


class TestTranslationLookup:
    def test_english_default(self):
        set_language("en")
        assert t("app.title") == "Kenshi Save Editor"

    def test_portuguese(self):
        set_language("pt")
        assert t("app.subtitle") == "EDITOR DE SAVES"

    def test_spanish(self):
        set_language("es")
        assert t("app.subtitle") == "EDITOR DE GUARDADOS"

    def test_unknown_key_returns_key(self):
        set_language("en")
        assert t("nonexistent.key") == "nonexistent.key"

    def test_missing_language_falls_back_to_english(self):
        set_language("fr")  # unsupported
        assert t("app.subtitle") == "SAVE EDITOR"

    def test_format_substitution(self):
        set_language("en")
        result = t("status.loaded", name="TestSave", files=3, records=100)
        assert "TestSave" in result
        assert "3" in result
        assert "100" in result

    def test_bad_format_kwargs_no_crash(self):
        set_language("en")
        # Missing required kwargs should not raise
        result = t("status.loaded")
        assert isinstance(result, str)


class TestLanguageState:
    def test_set_and_get(self):
        set_language("pt")
        assert get_language() == "pt"
        set_language("en")
        assert get_language() == "en"


class TestDetectLanguage:
    def test_portuguese_locale(self):
        with mock.patch("locale.getdefaultlocale", return_value=("pt_BR", "UTF-8")):
            assert detect_language() == "pt"

    def test_spanish_locale(self):
        with mock.patch("locale.getdefaultlocale", return_value=("es_ES", "UTF-8")):
            assert detect_language() == "es"

    def test_english_fallback(self):
        with mock.patch("locale.getdefaultlocale", return_value=("en_US", "UTF-8")):
            assert detect_language() == "en"

    def test_none_locale_fallback(self):
        with mock.patch("locale.getdefaultlocale", return_value=(None, None)):
            assert detect_language() == "en"

    def test_exception_fallback(self):
        with mock.patch("locale.getdefaultlocale", side_effect=ValueError):
            assert detect_language() == "en"


class TestTranslationCompleteness:
    """Every key should have translations for all supported languages."""

    def test_all_keys_have_all_languages(self):
        supported = {"en", "pt", "es"}
        missing = []
        for key, translations in TRANSLATIONS.items():
            for lang in supported:
                if lang not in translations:
                    missing.append(f"{key} missing '{lang}'")
        assert missing == [], f"Missing translations:\n" + "\n".join(missing)
