#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import os
import json
import threading
from datetime import datetime

# 路径对齐
from backend.llm.qwen_vl import QwenVLModel
from tts_ws import XF_TTS_Worker

class StreamingPopProcessor(Node):
    def __init__(self):
        super().__init__('streaming_pop_processor')
        
        # 1. 初始化模型与TTS
        self.model = QwenVLModel()
        # ！！！请务必填入真实的讯飞凭据！！！
        self.tts = XF_TTS_Worker(APPID='812ac76a', APIKey='46834d00f6389d11d8cb73206c756e72', APISecret='ODM1NTYyNDU3MGY0NmVlZjc1MjA2MjVi')
        
        # 2. 路径配置
        self.latest_image_path = "rviz_captured_images/latest.jpg"
        # 核心修复：确保 audio_dir 是绝对路径
        self.audio_dir = os.path.abspath(os.path.join(os.getcwd(), "data", "audio_out"))
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # 3. 记忆管理
        self.chat_history = [] # 用于保存上下文
        self.max_history = 10  # 最多保留5轮对话(10条记录)

        # 4. ROS 通信
        self.sub = self.create_subscription(String, '/asr/user_input', self.on_input, 10)
        self.tts_pub = self.create_publisher(String, '/xunfei/tts_play', 10)
        
        self.sentence_seps = ["。", "！", "？", "\n", "；", "!", "?", "..."]
        self.get_logger().info(f"✅ [波普先生] 语音存放路径: {self.audio_dir}")
        self.get_logger().info("✅ [波普先生] 已上线，记忆系统已启动。")

    def on_input(self, msg):
        user_text = msg.data.strip()
        if not user_text: return
        
        print(f"\n🎧 [ASR 输入]: {user_text}")

        # 检查图像
        image_data = None
        if os.path.exists(self.latest_image_path):
            with open(self.latest_image_path, "rb") as f:
                image_data = f.read()

        current_sentence = ""
        full_reply = ""
        print("🤖 [波普先生回复]: ", end="", flush=True)

        # --- 核心修改：带上下文的流式调用 ---
        # 这里的 identify_product_stream 需要在 qwen_vl.py 中修改以支持 history 参数
        generator = self.model.identify_product_stream(image_data, user_text, history=self.chat_history)

        for chunk in generator:
            print(chunk, end="", flush=True)
            current_sentence += chunk
            full_reply += chunk

            # 断句逻辑：只要有一句完整的话，立即合成语音
            if any(sep in chunk for sep in self.sentence_seps):
                text_to_speak = current_sentence.strip()
                if len(text_to_speak) > 1:
                    # 异步执行 TTS 合成与指令下达
                    threading.Thread(target=self.run_tts_and_play, args=(text_to_speak,)).start()
                current_sentence = ""

        # 扫尾处理
        if current_sentence.strip():
            self.run_tts_and_play(current_sentence.strip())

        # --- 更新记忆 ---
        self.chat_history.append({"role": "user", "content": user_text})
        self.chat_history.append({"role": "assistant", "content": full_reply})
        # 保持记忆长度
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]


    def run_tts_and_play(self, text):
        """合成 MP3 并按照机器人规范发布指令"""
        try:
            # 1. 生成文件名
            ts = datetime.now().strftime("%H%M%S_%f")
            audio_path = os.path.join(self.audio_dir, f"pop_{ts}.mp3")
            
            # 2. TTS 合成文件
            self.tts.generate(text, audio_path)
            
            # 3. 检查文件是否生成成功
            if os.path.exists(audio_path):
                # 4. 按照机器人文档要求的格式构建 JSON
                # 统一使用 append 模式实现流式队列播放
                play_cmd = {
                    "cmd": "append",
                    "file": audio_path
                }
                
                msg = String()
                msg.data = json.dumps(play_cmd)
                self.tts_pub.publish(msg)
                # self.get_logger().info(f"🔊 已发送播放指令: {audio_path}")
            else:
                self.get_logger().error(f"❌ TTS文件生成失败: {audio_path}")

        except Exception as e:
            self.get_logger().error(f"❌ 语音播报逻辑异常: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = StreamingPopProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()