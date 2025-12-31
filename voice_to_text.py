#!/usr/bin/env python3
import json
import os
import rclpy
import glob
from rclpy.node import Node
from std_msgs.msg import String
from datetime import datetime

# 路径对齐
SAVE_DIR = os.path.join(os.getcwd(), 'data', 'voice_to_text')
MAX_FILES = 50

class ASRMonitor(Node):
    def __init__(self):
        super().__init__('asr_monitor')
        self.subscription = self.create_subscription(String, '/xunfei/aiui_msg', self.msgs_callback, 10)
        self.text_publisher = self.create_publisher(String, '/asr/user_input', 10)
        
        self.last_processed_text = None
        self.last_processed_time = None

        os.makedirs(SAVE_DIR, exist_ok=True)
        self.get_logger().info(f"🎙️ [ASR启动] 路径: {SAVE_DIR}")

    def msgs_callback(self, msg: String):
        try:
            json_data = json.loads(msg.data)
            text = self.extract_text(json_data)
            
            if text and self.is_new_input(text):
                print(f"\n🎧 [拾音成功]: {text}")
                
                # 保存文本
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                with open(os.path.join(SAVE_DIR, f"asr_{ts}.txt"), 'w', encoding='utf-8') as f:
                    f.write(text)

                # 发布给大脑
                self.text_publisher.publish(String(data=text))
                self.last_processed_text = text
                self.last_processed_time = self.get_clock().now().nanoseconds
                self.cleanup()
        except Exception as e:
            self.get_logger().error(f"❌ ASR解析错误: {e}")

    def extract_text(self, data):
        try:
            # 适配讯飞AIUI嵌套格式
            content = data.get("content", {}).get("result", {})
            if "intent" in content: return content["intent"].get("text")
            # 备选路径
            sub_text = json.loads(content.get("cbm_meta", {}).get("text", "{}"))
            key = next(iter(sub_text))
            return json.loads(content.get(key, {}).get("text", "{}")).get('query')
        except: return None

    def is_new_input(self, text):
        if len(text) < 2: return False
        now = self.get_clock().now().nanoseconds
        if text == self.last_processed_text and (now - (self.last_processed_time or 0)) < 3e9:
            return False
        return True

    def cleanup(self):
        files = sorted(glob.glob(os.path.join(SAVE_DIR, "*.txt")), key=os.path.getmtime)
        while len(files) > MAX_FILES: os.remove(files.pop(0))

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(ASRMonitor())
    rclpy.shutdown()

if __name__ == '__main__':
    main()