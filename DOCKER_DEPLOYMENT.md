# FireAPRS Docker Deployment Guide

This guide explains how to deploy and run FireAPRS using Docker with two different scheduling options.

## Prerequisites

- Docker and Docker Compose installed
- Properly configured `config.ini` file with your APRS credentials

## Quick Start

1. **Build the Docker image:**
   ```bash
   ./deploy.sh build
   ```

2. **Configure your settings:**
   Edit `config.ini` with your APRS callsign, password, and other settings.

## Running Options

### Option 1: Crontab Scheduling (Recommended)

This runs the program once and exits, perfect for crontab scheduling:

```bash
# Run once manually
./deploy.sh run-once

# Get crontab setup instructions
./deploy.sh setup-cron
```

The crontab entry will run FireAPRS every 60 minutes:
```
0 * * * * cd /path/to/FireAPRS && docker-compose up fire-aprs >> /tmp/fire-aprs-cron.log 2>&1
```

To set this up:
1. Run `./deploy.sh setup-cron` to get the exact command
2. Run `crontab -e` to edit your crontab
3. Add the provided line
4. Save and exit

### Option 2: Auto-Schedule Mode

This runs the program with internal scheduling (stays running):

```bash
# Start with auto-scheduling (runs every 60 minutes)
./deploy.sh run-scheduled

# Check logs
./deploy.sh logs-scheduled

# Stop the scheduled service
./deploy.sh stop
```

## Management Commands

```bash
./deploy.sh build              # Build the Docker image
./deploy.sh run-once          # Run once (for crontab)
./deploy.sh run-scheduled     # Run with auto-scheduling
./deploy.sh stop              # Stop all containers
./deploy.sh logs              # Show logs (run-once mode)
./deploy.sh logs-scheduled    # Show logs (scheduled mode)
./deploy.sh setup-cron        # Get crontab instructions
./deploy.sh help              # Show all commands
```

## Configuration

Make sure to update `config.ini` with your settings:

```ini
[aprssend]
callsign = YOUR_CALLSIGN
password = YOUR_APRS_PASSWORD
# ... other settings
```

## Data Persistence

The Docker setup automatically creates and mounts these directories:
- `./data/` - For downloaded fire data
- `./logs/` - For application logs

## Choosing Between Crontab and Auto-Schedule

**Use Crontab when:**
- You want more control over scheduling
- You're running on a server with other cron jobs
- You prefer system-level scheduling
- You want to easily stop/start scheduling

**Use Auto-Schedule when:**
- You want a simple "set and forget" solution
- You're running in a dedicated container environment
- You don't want to manage crontab entries

## Troubleshooting

1. **Check logs:**
   ```bash
   ./deploy.sh logs
   # or
   ./deploy.sh logs-scheduled
   ```

2. **Verify configuration:**
   ```bash
   docker run --rm -v $(pwd)/config.ini:/app/config.ini fire-aprs:latest python main.py --help
   ```

3. **Test run:**
   ```bash
   ./deploy.sh run-once
   ```

## Examples

### Quick Test Run
```bash
./deploy.sh build
./deploy.sh run-once
```

### Production Setup with Crontab
```bash
./deploy.sh build
./deploy.sh setup-cron
# Follow the instructions to add to crontab
```

### Production Setup with Auto-Schedule
```bash
./deploy.sh build
./deploy.sh run-scheduled
# Service now runs continuously with 60-minute intervals
```
