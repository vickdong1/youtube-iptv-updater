import subprocess
import datetime

CHANNELS_FILE = "channels.txt"
OUTPUT_FILE = "youtube_live.m3u"
COOKIES_FILE = "cookies.txt"  # 必须在同目录下

def get_m3u8_url(youtube_url):
    """
    使用 yt-dlp 获取直播 m3u8 地址，传入 cookies
    """
    try:
        result = subprocess.run(
            ["yt-dlp", "--cookies", COOKIES_FILE, "-g", youtube_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ 获取失败: {youtube_url}\n{result.stderr.strip()}")
            return None
        url = result.stdout.strip().split("\n")[0]
        return url
    except Exception as e:
        print(f"❌ 获取异常: {youtube_url} ({e})")
        return None

def read_channels():
    """
    读取 channels.txt，每行格式:
    YouTube链接   # 频道名称
    """
    channels = []
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                url, name = line.split("#", 1)
                url = url.strip()
                name = name.strip()
                channels.append((url, name))
    return channels

def generate_m3u():
    channels = read_channels()
    m3u_lines = ["#EXTM3U"]
    for url, name in channels:
        print(f"▶ 正在获取：{name}")
        m3u8_url = get_m3u8_url(url)
        if m3u8_url:
            m3u_lines.append(f'#EXTINF:-1,{name}')
            m3u_lines.append(m3u8_url)
        else:
            print(f"❌ {name} 获取失败")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    print(f"✅ 已生成最新 {OUTPUT_FILE} ({timestamp})")

if __name__ == "__main__":
    generate_m3u()
