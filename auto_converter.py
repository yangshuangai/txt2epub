#!/usr/bin/env python3
import os
import time
import subprocess
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TXTHandler(FileSystemEventHandler):
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix.lower() == '.txt':
            logger.info(f"检测到新文件: {file_path}")
            self.process_file(file_path)
    
    def process_file(self, txt_file):
        try:
            # 调用原有的 run.py 脚本
            cmd = ['python', 'run.py', str(txt_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd='/app')
            
            if result.returncode == 0:
                logger.info(f"成功转换文件: {txt_file}")
                # 移动生成的文件到输出目录
                self.move_output_files(txt_file)
            else:
                logger.error(f"转换失败: {result.stderr}")
                
        except Exception as e:
            logger.error(f"处理文件时出错: {e}")
    
    def move_output_files(self, original_txt):
        """将生成的 epub/kepub 文件移动到输出目录"""
        # 根据你的 run.py 逻辑，生成的文件可能在相同目录
        base_name = original_txt.stem
        possible_extensions = ['.epub', '.kepub', '.azw3']
        
        for ext in possible_extensions:
            output_file = original_txt.parent / f"{base_name}{ext}"
            if output_file.exists():
                target_file = self.output_dir / f"{base_name}{ext}"
                output_file.rename(target_file)
                logger.info(f"移动文件到输出目录: {target_file}")

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # 确保目录存在
    Path(input_dir).mkdir(exist_ok=True)
    Path(output_dir).mkdir(exist_ok=True)
    
    # 处理已存在的文件
    for txt_file in Path(input_dir).glob("*.txt"):
        logger.info(f"处理现有文件: {txt_file}")
        cmd = ['python', 'run.py', str(txt_file)]
        subprocess.run(cmd, cwd='/app')
        # 移动生成的文件
        base_name = txt_file.stem
        for ext in ['.epub', '.kepub', '.azw3']:
            output_file = txt_file.parent / f"{base_name}{ext}"
            if output_file.exists():
                target_file = Path(output_dir) / f"{base_name}{ext}"
                output_file.rename(target_file)
    
    # 设置文件监控
    event_handler = TXTHandler(input_dir, output_dir)
    observer = Observer()
    observer.schedule(event_handler, input_dir, recursive=False)
    observer.start()
    
    logger.info(f"开始监控目录: {input_dir}")
    logger.info(f"输出目录: {output_dir}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("停止监控")
    observer.join()

if __name__ == "__main__":
    main()
