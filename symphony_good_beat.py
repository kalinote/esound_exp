import math
import struct
import wave

import matplotlib.pyplot as plt
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
    (None, 1, F_BEAT),   # 八分休止符
    ("G", 1, PP_BEAT),
    ("G", 1, P_BEAT),
    ("G", 1, PP_BEAT),
    ("Eb", 4, F_BEAT),  # 二分音符

    (None, 1, F_BEAT),   # 八分休止符
    ("F", 1, PP_BEAT),
    ("F", 1, P_BEAT),
    ("F", 1, PP_BEAT),
    ("D", 8, F_BEAT),    # 全音符
]

frequencies = {
    "G": 391.995,
    "Eb": 311.127,
    "F": 349.228,
    "D": 293.665,
}

def generate_note(note, units, beat):
    count = units * round(SAMPLE_RATE * 60 / (BPM * 2))

    # 休止符：所有采样值为 0
    if note is None:
        return b"\x00\x00" * count

    data = bytearray()

    # 4 毫秒淡入、淡出
    fade_samples = round(0.004 * SAMPLE_RATE)

    for n in range(count):
        t = n / SAMPLE_RATE
        x = AMPLITUDE * math.sin(2 * math.pi * frequencies[note] * t)

        # 线性振幅包络
        envelope = min(
            1.0,
            n / fade_samples,
            (count - 1 - n) / fade_samples,
        )

        # 淡入淡出包络
        x *= envelope
        # 力度系数
        x *= beat
        sample = round(x * 32767)
        data.extend(struct.pack("<h", sample))

    return bytes(data)

pcm = bytearray()

for note, units, beat in melody:
    pcm.extend(generate_note(note, units, beat))

# 写入 WAV 文件
with wave.open("symphony_good_beat.wav", "wb") as wav:
    wav.setnchannels(CHANNELS)
    wav.setsampwidth(BIT_DEPTH // 8)
    wav.setframerate(SAMPLE_RATE)
    wav.writeframes(pcm)


def plot_boundary(pcm, boundary_index=4, window_ms=5):
    samples = struct.unpack(f"<{len(pcm)//2}h", pcm)

    # 计算音符交界处的采样点位置
    boundary = sum(
        units for _, units, _ in melody[:boundary_index]
    ) * round(SAMPLE_RATE * 60 / (BPM * 2))

    # 截取交界处前后几毫秒
    window = int(SAMPLE_RATE * window_ms / 1000)
    start = boundary - window
    end = boundary + window

    x = [(i - boundary) / SAMPLE_RATE * 1000 for i in range(start, end)]
    y = samples[start:end]

    # 分别绘制交界处两侧的波形
    plt.figure(figsize=(12, 4))
    plt.plot(x[:window], y[:window], ".-", markersize=3, label="前一个音符")
    plt.plot(x[window:], y[window:], ".-", markersize=3, label="后一个音符")

    # 用红线连接交界处的两个采样点
    plt.plot(
        x[window-1:window+1],
        y[window-1:window+1],
        "r.-", linewidth=2, markersize=8,
        label="连接处采样点"
    )

    plt.axvline(0, color="red", linestyle="--", alpha=0.5)
    plt.xlabel("时间 (毫秒)")
    plt.ylabel("PCM采样点值")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()
    
plot_boundary(pcm, boundary_index=4, window_ms=10)

