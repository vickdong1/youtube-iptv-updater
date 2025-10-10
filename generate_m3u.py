import subprocess
import datetime

def get_stream_url(youtube_url):
    try:
        # 用 yt-dlp 获取真实 m3u8 播放地址
        result = subprocess.run(
            ["yt-dlp", "-g", youtube_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ 获取失败: {youtube_url} ({result.stderr.strip().splitlines()[-1]})")
            return None
    except Exception as e:
        print(f"❌ 异常: {youtube_url} ({e})")
        return None

def generate_m3u(channels_file, output_file):
    with open(channels_file, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    playlist = ["#EXTM3U"]
    for line in lines:
        if "#" in line:
            url, name = line.split("#", 1)
            url = url.strip()
            name = name.strip()
            print(f"▶ 正在获取：{name}")
            stream_url = get_stream_url(url)
            if stream_url:
                playlist.append(f'#EXTINF:-1 group-title="YouTube", {name}')
                playlist.append(stream_url)
                print(f"✅ 成功: {name}")
            else:
                print(f"❌ 获取失败: {url}")
        else:
            print(f"⚠️ 跳过无效行: {line}")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(playlist))
    print(f"✅ 已生成最新 {output_file} 文件 ({now})")

if __name__ == "__main__":
    generate_m3u("channels.txt", "youtube_live.m3u")
