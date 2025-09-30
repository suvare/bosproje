import os
import subprocess
import time
import json
from pathlib import Path

def setup_pm2_vscode():
    """VS Code için PM2 entegrasyonu"""
    
    # PM2 config dosyası
    pm2_config = {
        "apps": [{
            "name": "quantum-bot-vscode",
            "script": "bot.py",
            "interpreter": "python",
            "cwd": str(Path.cwd()),
            "instances": 1,
            "autorestart": True,
            "watch": False,
            "max_memory_restart": "500M",
            "env": {
                "VSCODE": "true"
            },
            "error_file": "./logs/vscode-err.log",
            "out_file": "./logs/vscode-out.log",
            "log_file": "./logs/vscode-combined.log"
        }]
    }
    
    # Config dosyasını yaz
    with open("ecosystem.vscode.json", "w") as f:
        json.dump(pm2_config, f, indent=2)
    
    print("✅ PM2 config VS Code için hazır!")
    print("🚀 Başlatmak için: pm2 start ecosystem.vscode.json")
    print("📊 VS Code Terminal'de çalıştırın!")

if __name__ == "__main__":
    setup_pm2_vscode()