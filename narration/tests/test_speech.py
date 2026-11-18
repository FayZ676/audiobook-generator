import sys
import types

import pytest

from tta_narration import speech
from tta_narration.speech import SpeechModel, load_speech_model


class Silent(SpeechModel):
    sample_rate = 8000

    def say(self, texts, voice):
        return []


class NotAModel:
    pass


@pytest.fixture(name="registered")
def register_fakes(monkeypatch):
    module = types.ModuleType("fake_models")
    module.Silent, module.NotAModel = Silent, NotAModel
    monkeypatch.setitem(sys.modules, "fake_models", module)
    monkeypatch.setattr(speech, "MODELS", {"silent": "fake_models:Silent", "wrong": "fake_models:NotAModel"})


@pytest.mark.usefixtures("registered")
def test_a_model_is_chosen_by_name_or_by_the_environment(monkeypatch):
    assert isinstance(load_speech_model("silent"), Silent)

    monkeypatch.setenv("TTA_SPEECH_MODEL", "silent")
    assert isinstance(load_speech_model(), Silent)


@pytest.mark.usefixtures("registered")
def test_an_unknown_name_lists_the_models_there_are():
    with pytest.raises(ValueError, match="silent, wrong"):
        load_speech_model("whisper")


@pytest.mark.usefixtures("registered")
def test_a_registered_class_must_subclass_the_contract():
    with pytest.raises(TypeError):
        load_speech_model("wrong")


def test_a_model_missing_part_of_the_contract_cannot_be_made():
    class NoSampleRate(SpeechModel):  # pylint: disable=abstract-method
        def say(self, texts, voice):
            return []

    with pytest.raises(TypeError, match="sample_rate"):
        NoSampleRate()  # pylint: disable=abstract-class-instantiated


def test_every_registered_model_names_a_class():
    for path in speech.MODELS.values():
        module, cls = path.split(":")
        assert module.startswith("tta_narration.models.") and cls
