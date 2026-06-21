"""LifeBeyond 静态文件服务器
- 直接由 vefaas / 本地 dev 调用，避免 sh -c 与环境变量展开带来的部署兼容问题。
- 监听 0.0.0.0 + 环境变量 DEPLOY_RUN_PORT（缺省 5000），适配多 worktree。
"""
import os
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


def main() -> None:
    port_raw = os.environ.get("DEPLOY_RUN_PORT", "5000").strip()
    try:
        port = int(port_raw)
    except ValueError:
        port = 5000

    # 保证工作目录就是当前脚本所在目录（vefaas 启动时 cwd 可能与项目根不同）
    root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root)

    handler = SimpleHTTPRequestHandler
    httpd = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"[server] Serving HTTP on 0.0.0.0:{port} (cwd={root})", flush=True)
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("[server] shutting down", flush=True)
        httpd.shutdown()


if __name__ == "__main__":
    main()
