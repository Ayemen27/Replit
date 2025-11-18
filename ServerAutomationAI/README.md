# AI Multi-Agent Server Automation System

An intelligent, autonomous server management system powered by multiple specialized AI agents working together to monitor, maintain, and protect your infrastructure.

## 🤖 Overview

This system deploys 6 specialized AI agents that work collaboratively to:
- Monitor system performance (CPU, RAM, Disk, Network)
- Analyze logs for errors and security threats
- Detect and respond to security incidents
- Manage databases (PostgreSQL/MongoDB)
- Perform automated backups and recovery
- Send real-time alerts via Telegram and Email

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              AI Manager (Central Hub)               │
│         Coordinates all agents & decisions          │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
   ┌────▼────┐         ┌────▼────┐
   │ Monitor │         │ Analyze │
   │ Agents  │         │ Agents  │
   └────┬────┘         └────┬────┘
        │                   │
   ┌────┴────────┬──────────┴───────┬────────┐
   │             │                  │        │
┌──▼──┐    ┌────▼─────┐    ┌───────▼──┐  ┌──▼────┐
│Perf │    │Security  │    │Database  │  │Backup │
│Mon  │    │Monitor   │    │Manager   │  │Agent  │
└─────┘    └──────────┘    └──────────┘  └───────┘
```

## 📦 Installation

### Quick Start

```bash
# Clone or download the project
cd /srv/ai_system/

# Install dependencies
pip install -r requirements.txt

# Configure settings
nano configs/config.yaml

# Run the system
python main.py start
```

### Requirements

- Python 3.9+
- Linux-based system
- PostgreSQL (optional)
- MongoDB (optional)

## ⚙️ Configuration

Edit `configs/config.yaml` to configure:

1. **Database Settings** (PostgreSQL/MongoDB)
2. **Notification Channels** (Telegram/Email)
3. **Monitoring Thresholds** (CPU, Memory, Disk)
4. **Agent Settings** (Enable/disable, intervals)
5. **Backup Configuration** (Schedule, retention)

### Example: Enable Telegram Notifications

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN_HERE"
    chat_id: "YOUR_CHAT_ID_HERE"
```

## 🚀 Usage

### Start the System

```bash
python main.py start
```

### Check Status

```bash
python main.py status
```

### Test Individual Agents

```bash
python agents/performance_monitor.py
python agents/security_monitor.py
```

## 📊 Agents Description

### 1. AI Manager
Central coordinator that manages all other agents, aggregates alerts, and makes system-wide decisions.

### 2. Performance Monitor
Monitors CPU, RAM, Disk, and Network usage with configurable thresholds.

### 3. Log Analyzer
Analyzes system logs for errors, warnings, and security events using pattern matching.

### 4. Security Monitor
Detects failed login attempts, suspicious processes, and insecure file permissions.

### 5. Database Manager
Monitors PostgreSQL and MongoDB health, connections, and performs maintenance.

### 6. Backup & Recovery
Automated backups of databases, configs, and logs with compression and retention management.

## 🔔 Notifications

The system supports multiple notification channels:

- **Telegram**: Real-time alerts via Telegram Bot
- **Email**: SMTP-based email notifications
- **Logs**: All events logged to `/srv/ai_system/logs/`

## 📁 Project Structure

```
/srv/ai_system/
├── agents/              # AI agent implementations
├── tools/               # Utility modules
├── configs/             # Configuration files
├── logs/                # System logs
├── backups/             # Backup storage
├── src/setup/           # Setup scripts
├── agent_manager.py     # Agent lifecycle manager
├── main.py              # Main entry point
└── requirements.txt     # Python dependencies
```

## 🔒 Security

- Stores sensitive credentials in config.yaml (keep secure)
- Monitors for security threats continuously
- Detects brute-force login attempts
- Alerts on suspicious activities
- File permission monitoring

## 📈 Performance

- Lightweight design (<100MB RAM per agent)
- Configurable check intervals
- Async communication between agents
- Efficient log parsing
- Minimal CPU overhead

## 🛠️ Troubleshooting

### Agents not starting?
Check logs in `/srv/ai_system/logs/` for errors.

### No notifications?
Verify Telegram/Email settings in `config.yaml`.

### Database connection errors?
Ensure PostgreSQL credentials are correct.

### Permission denied errors?
Some features require sudo/root access.

## 📝 Logs

All agents log to `/srv/ai_system/logs/`:
- `ai_manager.log`
- `performance_monitor.log`
- `security_monitor.log`
- `database_manager.log`
- `backup_recovery.log`
- `log_analyzer.log`

## 🤝 Contributing

This is a bootstrap system designed to be extended. Future enhancements:
- Web dashboard
- Advanced AI/ML capabilities
- More integrations (Slack, SMS)
- Predictive analytics

## 📄 License

This project is part of the AI Multi-Agent Server Automation System.

## 📞 Support

For issues and questions:
1. Check `PROGRESS.md` for detailed information
2. Review logs in `/srv/ai_system/logs/`
3. Test individual agents for debugging

---

**Version**: 1.0.0  
**Status**: Bootstrap Complete ✓  
**Last Updated**: 2025-11-14
