import math
import struct
import wave

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

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

def plot_boundary(pcm, boundary_index=4, window_ms=5):
    samples = struct.unpack(f"<{len(pcm)//2}h", pcm)

    # 计算音符交界处的采样点位置
    boundary = sum(
        units for _, units in melody[:boundary_index]
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

pcm = bytearray()

for note, units in melody:
    pcm.extend(generate_note(note, units))

# 写入 WAV 文件
with wave.open("symphony_good.wav", "wb") as wav:
    wav.setnchannels(CHANNELS)
    wav.setsampwidth(BIT_DEPTH // 8)
    wav.setframerate(SAMPLE_RATE)
    wav.writeframes(pcm)


def plot_boundary(pcm, boundary_index=4, window_ms=5):
    samples = struct.unpack(f"<{len(pcm)//2}h", pcm)

    # 计算音符交界处的采样点位置
    boundary = sum(
        units for _, units in melody[:boundary_index]
    ) * round(SAMPLE_RATE * 60 / (BPM * 2))

    # 截取交界处前后几毫秒
    window = int(SAMPLE_RATE * window_ms / 1000)
    start = boundary - window
    end = boundary + window

    x = [(i - boundary) / SAMPLE_RATE * 1000 for i in range(start, end)]
    y = samples[start:end]

    # 分别绘制交界处两侧的波形
    plt.figure(figsize=(12, 4))
    plt.plot(x[:window], y[:window], ".-", markersize=3, label="Before")
    plt.plot(x[window:], y[window:], ".-", markersize=3, label="After")

    # 用红线连接交界处的两个采样点
    plt.plot(
        x[window-1:window+1],
        y[window-1:window+1],
        "r.-", linewidth=2, markersize=8,
        label="Boundary"
    )

    plt.axvline(0, color="red", linestyle="--", alpha=0.5)
    plt.xlabel("Time relative to boundary (ms)")
    plt.ylabel("PCM Value")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()
    
plot_boundary(pcm, boundary_index=4, window_ms=5)

