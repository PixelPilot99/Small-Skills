import requests
import os
import sys

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
    
    # 读取环境变量（同时检查用户变量和系统变量）
    api_key = os.environ.get("SKILL_ASR_API_KEY")
    if not api_key:
        raise ValueError("环境变量 SKILL_ASR_API_KEY 未设置")
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # 获取文件名和扩展名
    file_name = os.path.basename(file_path)
    
    with open(file_path, "rb") as audio_file:
        files = {
            "file": (file_name, audio_file),
            "model": (None, "FunAudioLLM/SenseVoiceSmall")
        }
        response = requests.post(url, headers=headers, files=files)
    
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


if __name__ == "__main__":
    # 命令行调用: python script.py <file_path> <output_path>
    if len(sys.argv) != 3:
        print("用法: python script.py <音频文件路径> <输出txt路径>")
        print("示例: python script.py audio.mp3 output/result.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    text = transcribe_audio(input_file, output_file)
    print(f"转录内容:\n{text}")
