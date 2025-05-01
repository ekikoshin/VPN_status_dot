import sys
import tkinter as tk
import subprocess

VPN_NAME = "VPB@Home"  # 你的 VPN 适配器名称

class VPNStatusIndicator:
    def __init__(self, root):
        self.root = root
        self.root.title("VPN Status")
        self.root.attributes("-topmost", True)  # 窗口始终置顶
        self.root.overrideredirect(True)  # 无边框窗口
        self.root.geometry("50x50+0+1200")  # 设定窗口位置 (左下角)

        self.canvas = tk.Canvas(root, width=50, height=50, bg="black", highlightthickness=0)
        self.canvas.pack()

        self.is_red = True  # 控制红色灯光闪烁
        self.vpn_connected = False  # 记录VPN状态

        # 绑定右键菜单
        self.root.bind("<Button-3>", self.show_menu)
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="关闭", command=self.root.quit)

        self.update_vpn_status()

    def check_vpn(self):
        """ 通过 PowerShell 或 nmcli 检测 VPN 是否连接 """
        try:
            if sys.platform.startswith("win"):
                # Windows: 使用 PowerShell 获取 VPN 状态
                command = [
                    "powershell", "-Command",
                    f"Get-VPNConnection -Name '{VPN_NAME}' | Select-Object -ExpandProperty ConnectionStatus"
                ]
                result = subprocess.run(command, capture_output=True, text=True, startupinfo=self.get_hidden_terminal())

                return "Connected" in result.stdout  # 如果输出包含 "Connected"，表示 VPN 连接
            else:
                # Linux/macOS: 使用 nmcli 检测 VPN 状态
                command = ["nmcli", "connection", "show", "--active"]
                result = subprocess.run(command, capture_output=True, text=True)
                return VPN_NAME in result.stdout

        except Exception as e:
            print(f"Error checking VPN status: {e}")
        return False

    def update_vpn_status(self):
        """ 更新 VPN 指示灯，红灯闪烁 """
        new_status = self.check_vpn()
        
        if new_status:
            # VPN 连接，红灯闪烁
            self.is_red = not self.is_red
            color = "red" if self.is_red else "black"
        else:
            # VPN 未连接，绿色常亮
            color = "green"
            self.is_red = True  # 确保红灯恢复默认状态

        self.canvas.delete("all")
        self.canvas.create_oval(5, 5, 45, 45, fill=color, outline=color)

        self.root.after(1000 if new_status else 5000, self.update_vpn_status)  # VPN 连接时 1 秒闪烁，断开时 5 秒更新

    def get_hidden_terminal(self):
        """ 隐藏 PowerShell 窗口（仅 Windows 有效） """
        if sys.platform.startswith("win"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            return startupinfo
        return None

    def show_menu(self, event):
        """ 右键显示菜单 """
        self.menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    root = tk.Tk()
    app = VPNStatusIndicator(root)
    root.mainloop()
