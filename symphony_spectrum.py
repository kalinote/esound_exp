import math
import struct
import wave

import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

F_BEAT = 1.25
P_BEAT = 0.8
PP_BEAT = 0.5

SAMPLE_RATE = 44100
BIT_DEPTH = 16
CHANNELS = 1
BPM = 160
AMPLITUDE = 0.5

melody = [
    (None, 1, F_BEAT),  # 八分休止符
    ("G", 1, PP_BEAT),
    ("G", 1, P_BEAT),
    ("G", 1, PP_BEAT),
    ("Eb", 4, F_BEAT),  # 二分音符

    (None, 1, F_BEAT),  # 八分休止符
    ("F", 1, PP_BEAT),
    ("F", 1, P_BEAT),
    ("F", 1, PP_BEAT),
    ("D", 8, F_BEAT),   # 全音符
]

frequencies = {
    "G": 391.995,
    "Eb": 311.127,
    "F": 349.228,
    "D": 293.665,
}

harmonics = [1.0, 0.5, 0.25, 0.125]


def generate_note(note, units, beat, harmonic_weights=None):
    """生成浮点波形"""
    count = units * round(SAMPLE_RATE * 60 / (BPM * 2))

    if note is None:
        return [0.0] * count

    weights = harmonics if harmonic_weights is None else harmonic_weights
    norm = math.sqrt(sum(a * a for a in weights))
    coefficients = [a / norm for a in weights] if norm else []
    active = [
        (k, a) for k, a in enumerate(coefficients, start=1)
        if a != 0 and k * frequencies[note] < SAMPLE_RATE / 2
    ]

    fade_samples = round(0.004 * SAMPLE_RATE)
    samples = []

    for n in range(count):
        t = n / SAMPLE_RATE
        envelope = min(1.0, n / fade_samples, (count - 1 - n) / fade_samples)
        wave_value = sum(
            a * math.sin(2 * math.pi * k * frequencies[note] * t)
            for k, a in active
        )
        samples.append(AMPLITUDE * beat * envelope * wave_value)

    return samples


def plot_waveform(samples, title="", ax=None, start_ms=15, duration_ms=20):
    """绘制浮点波形，避免 PCM 量化影响。"""
    ax = ax if ax is not None else plt.subplots()[1]
    start = round(start_ms * SAMPLE_RATE / 1000)
    end = min(len(samples), start + round(duration_ms * SAMPLE_RATE / 1000))
    times = np.arange(start, end) / SAMPLE_RATE * 1000

    ax.plot(times, samples[start:end])
    ax.set(title=f"{title} · 波形", xlabel="时间 (ms)", ylabel="振幅")
    ax.grid(alpha=0.3)
    return ax


def plot_spectrum(samples, title="", ax=None, start_ms=15, duration_ms=150, max_hz=2500):
    """对稳定片段进行 FFT，绘制单边振幅频谱。"""
    ax = ax if ax is not None else plt.subplots()[1]
    start = round(start_ms * SAMPLE_RATE / 1000)
    end = min(len(samples), start + round(duration_ms * SAMPLE_RATE / 1000))
    signal = np.asarray(samples[start:end], dtype=float)
    if len(signal) < 2:
        raise ValueError("所选片段太短，无法计算频谱")

    window = np.hanning(len(signal))
    spectrum = np.abs(np.fft.rfft(signal * window)) * 2 / window.sum()
    freqs = np.fft.rfftfreq(len(signal), d=1 / SAMPLE_RATE)

    ax.plot(freqs, spectrum)
    ax.set(xlim=(0, max_hz), title=f"{title} · 频谱", xlabel="频率 (Hz)", ylabel="振幅")
    ax.grid(alpha=0.3)
    return ax


def plot_boundary(pcm, boundary_index=4, window_ms=5):
    """音符交界处采样点图"""
    samples = struct.unpack(f"<{len(pcm) // 2}h", pcm)
    boundary = sum(units for _, units, _ in melody[:boundary_index]) * round(
        SAMPLE_RATE * 60 / (BPM * 2)
    )
    window = round(SAMPLE_RATE * window_ms / 1000)
    start, end = boundary - window, boundary + window
    times = [(i - boundary) / SAMPLE_RATE * 1000 for i in range(start, end)]
    values = samples[start:end]

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(times[:window], values[:window], ".-", markersize=3, label="前一个音符")
    ax.plot(times[window:], values[window:], ".-", markersize=3, label="后一个音符")
    ax.plot(times[window - 1:window + 1], values[window - 1:window + 1],
            "r.-", linewidth=2, markersize=8, label="连接处采样点")
    ax.axvline(0, color="red", linestyle="--", alpha=0.5)
    ax.set(xlabel="时间 (毫秒)", ylabel="PCM 采样点值")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return ax


# 1. 音符 -> 浮点波形 -> PCM -> WAV
samples = []
for note, units, beat in melody:
    samples.extend(generate_note(note, units, beat))


pcm_samples = [round(max(-1.0, min(1.0, x)) * 32767) for x in samples]
pcm = struct.pack(f"<{len(pcm_samples)}h", *pcm_samples)

with wave.open("symphony_good_beat_harmonic.wav", "wb") as wav:
    wav.setnchannels(CHANNELS)
    wav.setsampwidth(BIT_DEPTH // 8)
    wav.setframerate(SAMPLE_RATE)
    wav.writeframes(pcm)
plot_boundary(pcm, boundary_index=4, window_ms=10)

# 2. 更换谐波权重，比较同一个 G 音的波形和频谱
timbres = {
    "纯音": [1.0],
    "1～4 次谐波": [1.0, 0.5, 0.25, 0.125],
    "奇次谐波": [1.0, 0.0, 0.5, 0.0, 0.25],
}
fig, axes = plt.subplots(len(timbres), 2, figsize=(12, 9))
for i, (name, weights) in enumerate(timbres.items()):
    note_samples = generate_note("G", 1, 1.0, harmonic_weights=weights)
    plot_waveform(note_samples, name, ax=axes[i, 0])
    plot_spectrum(note_samples, name, ax=axes[i, 1])
fig.tight_layout()
plt.show()
