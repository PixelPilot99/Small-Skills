import os
import sys

import requests


def transcribe_audio(file_path: str, output_path: str) -> str:
    """
    语音转文字，结果保存为txt文件

    Args:
        file_path: 音频文件路径
        output_path: 输出txt文件路径

    Returns:
        转录的文字内容
    """
    url = "https://api.siliconflow.cn/v1/audio/transcriptions"

    api_key = os.environ.get("SKILL_ASR_API_KEY")
    if not api_key:
        raise ValueError("环境变量 SKILL_ASR_API_KEY 未设置（设置方法见技能文档，切勿暴露密钥内容）")

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    file_name = os.path.basename(file_path)

    try:
        with open(file_path, "rb") as audio_file:
            files = {
                "file": (file_name, audio_file),
                "model": (None, "FunAudioLLM/SenseVoiceSmall")
            }
            response = requests.post(url, headers=headers, files=files, timeout=300)

        response.raise_for_status()
        result = response.json()
        transcribed_text = result.get("text", "")

        # 保存结果到txt
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcribed_text)

        print(f"转录完成，结果已保存至: {output_path}")
        return transcribed_text

    except requests.exceptions.Timeout:
        raise Exception("API请求超时，请检查网络连接或稍后重试")
    except requests.exceptions.ConnectionError:
        raise Exception("网络连接失败，请检查网络连接")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status in (401, 403):
            raise Exception(
                "API认证失败，请检查 SKILL_ASR_API_KEY 是否正确"
                "（不要在任何地方暴露密钥内容）"
            )
        elif status == 413:
            raise Exception("音频文件过大，请截取片段后重试")
        else:
            raise Exception(f"API请求失败（HTTP {status}），请稍后重试")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API请求异常: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python script.py <音频文件路径> <输出txt路径>")
        print("示例: python script.py audio.mp3 output/result.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        text = transcribe_audio(input_file, output_file)
        print(f"转录内容:\n{text}")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
