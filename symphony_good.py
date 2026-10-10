import math
import struct
import wave

SAMPLE_RATE = 44100
BIT_DEPTH = 16
CHANNELS = 1
BPM = 160
AMPLITUDE = 0.5

melody = [
    (None, 1),   # 八分休止符
    ("G", 1),
    ("G", 1),
    ("G", 1),
    ("Eb", 4),   # 二分音符

    (None, 1),   # 八分休止符
    ("F", 1),
    ("F", 1),
    ("F", 1),
    ("D", 8),    # 全音符
]

frequencies = {
    "G": 391.995,
    "Eb": 311.127,
    "F": 349.228,
    "D": 293.665,
}

def generate_note(note, units):
    count = units * round(SAMPLE_RATE * 60 / (BPM * 2))

    if note is None:
        return b"\x00\x00" * count

    data = bytearray()

    # 8 毫秒淡入、淡出
    fade_samples = round(0.008 * SAMPLE_RATE)

    for n in range(count):
        t = n / SAMPLE_RATE
        x = AMPLITUDE * math.sin(2 * math.pi * frequencies[note] * t)

        # 避免音符衔接处波形突变
        envelope = min(
            1.0,
            n / fade_samples,
            (count - 1 - n) / fade_samples,
        )

        x *= envelope
        sample = round(x * 32767)
        data.extend(struct.pack("<h", sample))

    return bytes(data)

pcm = bytearray()

for note, units in melody:
    pcm.extend(generate_note(note, units))

# 写入 WAV 文件
with wave.open("symphony_good.wav", "wb") as wav:
    wav.setnchannels(CHANNELS)
    wav.setsampwidth(BIT_DEPTH // 8)
    wav.setframerate(SAMPLE_RATE)
    wav.writeframes(pcm)
