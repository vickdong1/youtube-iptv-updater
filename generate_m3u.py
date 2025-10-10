import subprocess
import datetime

OUTPUT_FILE = "youtube_live.m3u"
CHANNEL_FILE = "channels.txt"

def get_stream_url(youtube_url):
    try:
        cmd = ["yt-dlp", "-g", youtube_url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        url = result.stdout.strip()
        return url
    except Exception as e:
        print(f"❌ 获取失败: {youtube_url}, 错误: {e}")
        return None

def main():
    with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
        channels = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    m3u_lines = ["#EXTM3U"]
    for ch in channels:
        print(f"正在更新: {ch}")
        stream_url = get_stream_url(ch)
        if stream_url:
            m3u_lines.append(f"#EXTINF:-1, {ch}")
            m3u_lines.append(stream_url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    print(f"✅ 已生成最新 {OUTPUT_FILE} 文件 ({datetime.datetime.now()})")

if __name__ == "__main__":
    main()
