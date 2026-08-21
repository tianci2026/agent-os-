"""Agent OS Web UI 启动脚本（纯 stdlib）。

用法：
    python serve_ui.py [store_dir] [port]

默认：
    store_dir = ./data/webui
    port      = 8787

启动后在浏览器打开 http://127.0.0.1:8787
先在 Settings 点「测试连接」探活 Ollama 并回填模型列表，再回 Composer 选工作区发消息。
"""
import sys

from agent_os.web_api import create_server, build_base_url, probe_ollama


def main():
    store = sys.argv[1] if len(sys.argv) > 1 else "./data/webui"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8787
    host = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1"

    server = create_server(store, host=host, port=port)
    print(f"Agent OS Web UI -> http://{host}:{port}")
    print(f"记忆存储目录       -> {store}")
    if server.auth.auth_enabled:
        _tok = server.admin_token
        if _tok:
            print(f"Admin token       -> {_tok}")
            print("  前端 Settings 填入此 token；或设 AGENT_OS_AUTH=0 关闭鉴权（仅本地开发）")
        else:
            print("Admin token       -> （已存在，请使用首次启动签发的 token；重置请删除 tenants.json）")

    # 启动时顺带探活一次 Ollama，把可用模型打到控制台方便选择
    try:
        info = probe_ollama(build_base_url("localhost", "11434"))
        print(f"Ollama 在线        -> {info['url']} · {info['latency']}ms")
        for m in info["models"]:
            print(f"  · {m}")
    except Exception as e:  # noqa: BLE001
        print(f"Ollama 未探活       -> {e!r}（可稍后在页面 Settings 重试）")

    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
        server.server_close()


if __name__ == "__main__":
    main()