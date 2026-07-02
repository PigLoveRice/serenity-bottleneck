#!/bin/bash
# Serenity cron setup script
# 安装 systemd timer，每天 18:30 自动运行筛选

set -e

SERVICE_DIR="/etc/systemd/system"

cp /home/serenity-bottleneck/scripts/serenity-daily.service "$SERVICE_DIR/"
cp /home/serenity-bottleneck/scripts/serenity-daily.timer "$SERVICE_DIR/"

systemctl daemon-reload
systemctl enable serenity-daily.timer
systemctl start serenity-daily.timer

echo "✅ Serenity 每日定时任务已安装"
echo "   时间: 每天 18:30 (UTC+8)"
echo "   日志: /var/log/serenity-daily.log"
echo ""
echo "管理命令:"
echo "   systemctl status serenity-daily.timer"
echo "   systemctl stop serenity-daily.timer"
echo "   journalctl -u serenity-daily.service -f"
