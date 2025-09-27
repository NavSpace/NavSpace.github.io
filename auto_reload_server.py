#!/usr/bin/env python3
"""
自动重载开发服务器
当文件发生变化时自动刷新浏览器页面
"""

import http.server
import socketserver
import os
import time
import threading
from pathlib import Path
import hashlib

class AutoReloadHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # 添加自动刷新的 JavaScript 代码
        if self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        # 如果请求的是HTML文件，注入自动刷新脚本
        if self.path.endswith('.html') or self.path == '/':
            try:
                if self.path == '/':
                    file_path = 'index.html'
                else:
                    file_path = self.path.lstrip('/')
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 注入自动刷新脚本
                auto_reload_script = '''
<script>
(function() {
    let lastModified = null;
    
    function checkForUpdates() {
        fetch(window.location.href, {
            method: 'HEAD',
            cache: 'no-cache'
        })
        .then(response => {
            const currentModified = response.headers.get('last-modified');
            if (lastModified && currentModified && lastModified !== currentModified) {
                console.log('文件已更新，正在刷新页面...');
                window.location.reload();
            }
            lastModified = currentModified;
        })
        .catch(console.error);
    }
    
    // 每30秒检查一次更新
    setInterval(checkForUpdates, 30000);
    
    // 页面加载时初始化
    checkForUpdates();
    
    console.log('自动刷新功能已启用，每3秒检查一次文件更新');
})();
</script>
'''
                
                # 在 </head> 前插入脚本
                if '</head>' in content:
                    content = content.replace('</head>', auto_reload_script + '\n</head>')
                else:
                    # 如果没有 </head>，在 <body> 前插入
                    content = content.replace('<body>', auto_reload_script + '\n<body>')
                
                # 发送响应
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                self.send_header('Last-Modified', self.date_time_string(os.path.getmtime(file_path)))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                return
                
            except FileNotFoundError:
                pass
        
        # 对于其他文件，使用默认处理
        super().do_GET()

def start_server(port=8000):
    """启动自动重载服务器"""
    print(f"启动自动重载开发服务器...")
    print(f"访问地址: http://localhost:{port}/index.html")
    print("文件更改时浏览器会自动刷新")
    print("按 Ctrl+C 停止服务器")
    
    with socketserver.TCPServer(("", port), AutoReloadHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")

if __name__ == "__main__":
    start_server()
