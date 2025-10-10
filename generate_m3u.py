import subprocess
import json
import datetime
import re
import sys

OUTPUT_FILE = "youtube_live.m3u"
CHANNEL_FILE = "channels.txt"


def get_stream_url(youtube_url):
    """通过 yt-dlp 获取直播流地址"""
    try:
        cmd = ["yt-dlp", "-J", "--no-warnings", youtube_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0 or not result.stdout.strip():
            print(f"❌ 获取失败: {youtube_url} (命令执行失败)")
            return None

        info = json.loads(result.stdout)
        if isinstance(info, list):
            info = info[0]

        # 1️⃣ 直接 URL
        if "url" in info:
            return info["url"]

        # 2️⃣ hlsManifestUrl（直播最常见）
        if "hlsManifestUrl" in info:
            return info["hlsManifestUrl"]

        # 3️⃣ 从 formats 里找 m3u8 流
        if "formats" in info:
            for f in reversed(info["formats"]):
                if "m3u8" in f.get("url", ""):
                    return f["url"]

        print(f"⚠️ 未找到直播流: {youtube_url}")
        return None

    except Exception as e:
        print(f"❌ 解析异常: {youtube_url} ({e})")
        return None


def extract_title_from_line(line):
    """提取 # 注释后的频道名"""
    m = re.search(r"#\s*(.*)$", line)
    return m.group(1).strip() if m else line


def main():
    try:
        with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
            channels = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"❌ 未找到 {CHANNEL_FILE}")
        sys.exit(1)

    m3u_lines = ["#EXTM3U"]
    for ch in channels:
        title = extract_title_from_line(ch)
        youtube_url = ch.split("#")[0].strip()

        print(f"▶ 正在获取：{title}")
        stream_url = get_stream_url(youtube_url)
        if stream_url:
            m3u_lines.append(f"#EXTINF:-1, {title}")
            m3u_lines.append(stream_url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    print(f"\n✅ 已生成最新 {OUTPUT_FILE} 文件 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")


if __name__ == "__main__":
    main()
