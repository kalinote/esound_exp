
import math
import wave
import struct

# 频率 400Hz A4
frequency = 440
# 采样率
sample_rate = 44100
# 持续时间
duration = 1.0
# 振幅
amplitude = 0.5

samples = []

for n in range(int(sample_rate * duration)):
    t = n / sample_rate

    # 正弦波
    x = amplitude * math.sin(2 * math.pi * frequency * t)

    # 转换为 16-bit 有符号整数 PCM
    sample = round(x * 32767)

    samples.append(sample)

# 保存 WAV
with wave.open("sine_440hz.wav", "wb") as wav:
    wav.setnchannels(1)       # 单声道
    wav.setsampwidth(2)       # 16-bit = 2 bytes
    wav.setframerate(sample_rate)

    for sample in samples:
        wav.writeframesraw(struct.pack("<h", sample))
