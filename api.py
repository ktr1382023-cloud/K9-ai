import torch
import torch.nn as nn
from dataclasses import asdict

from .utils.audio import LogMelSpectrogram
from .config import ModelConfig, MelConfig
from .models.model import StableTTS

from .text import symbols
from .text import cleaned_text_to_sequence
from .text.burmese import burmese_to_ipa2
from .datas.dataset import intersperse
from .utils.audio import load_and_resample_audio


def get_vocoder(model_path, model_name='vocos'):
    if model_name == 'vocos':
        from .vocoders.vocos.models.model import Vocos
        from .config import VocosConfig, MelConfig
        vocoder = Vocos(VocosConfig(), MelConfig())
        vocoder.load_state_dict(torch.load(model_path, weights_only=True, map_location='cpu'))
        vocoder.eval()
    else:
        raise NotImplementedError(f"Unsupported vocoder: {model_name}")
    return vocoder


class StableTTSAPI(nn.Module):
    def __init__(self, tts_model_path, vocoder_model_path, vocoder_name='vocos'):
        super().__init__()
        self.mel_config = MelConfig()
        self.tts_model_config = ModelConfig()

        self.mel_extractor = LogMelSpectrogram(**asdict(self.mel_config))

        self.tts_model = StableTTS(len(symbols), self.mel_config.n_mels, **asdict(self.tts_model_config))

        if tts_model_path.endswith(".safetensors"):
            from safetensors.torch import load_file
            state = load_file(tts_model_path)
        else:
            state = torch.load(tts_model_path, map_location='cpu', weights_only=True)
        self.tts_model.load_state_dict(state)
        self.tts_model.eval()

        self.vocoder_model = get_vocoder(vocoder_model_path, vocoder_name)
        self.vocoder_model.eval()

        self.g2p_mapping = {
            'burmese': burmese_to_ipa2,
        }
        self.supported_languages = self.g2p_mapping.keys()

    @torch.inference_mode()
    def inference(self, text, ref_audio, language, step, temperature=1.0,
                  length_scale=1.0, solver=None, cfg=3.0):
        device = next(self.parameters()).device
        phonemizer = self.g2p_mapping.get(language)
        if phonemizer is None:
            raise ValueError(f"Unsupported language: {language}")

        text = phonemizer(text)
        text = torch.tensor(
            intersperse(cleaned_text_to_sequence(text), item=0),
            dtype=torch.long, device=device
        ).unsqueeze(0)
        text_length = torch.tensor([text.size(-1)], dtype=torch.long, device=device)

        ref_audio = load_and_resample_audio(ref_audio, self.mel_config.sample_rate).to(device)
        ref_audio = self.mel_extractor(ref_audio)

        mel_output = self.tts_model.synthesise(
            text, text_length, step, temperature, ref_audio,
            length_scale, solver, cfg
        )['decoder_outputs']
        audio_output = self.vocoder_model(mel_output)
        return audio_output.cpu(), mel_output.cpu()

    def get_params(self):
        tts_param = sum(p.numel() for p in self.tts_model.parameters()) / 1e6
        vocoder_param = sum(p.numel() for p in self.vocoder_model.parameters()) / 1e6
        return tts_param, vocoder_param
