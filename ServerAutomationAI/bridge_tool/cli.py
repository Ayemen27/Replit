#!/usr/bin/env python3
"""
Bridge Tool - CLI Entry Point
Deploy and manage AI Multi-Agent System on production server
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge_tool.config_loader import ConfigLoader
from bridge_tool.services.ssh_client import SSHClientManager
from bridge_tool.services.sync_manager import SyncManager
from bridge_tool.commands import push, pull, status, execute, rollback, init


def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description='Bridge Tool - Deploy and manage AI Multi-Agent System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 bridge_tool/cli.py init              # Initialize configuration
  python3 bridge_tool/cli.py push              # Deploy to production
  python3 bridge_tool/cli.py push --dry-run    # Test deployment without changes
  python3 bridge_tool/cli.py status            # Check system status
  python3 bridge_tool/cli.py pull logs         # Download logs from server
  python3 bridge_tool/cli.py exec "python3 main.py status"  # Run command
  python3 bridge_tool/cli.py rollback          # Rollback to previous release
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize bridge configuration')
    
    # Push command
    push_parser = subparsers.add_parser('push', help='Deploy to production server')
    push_parser.add_argument('--dry-run', action='store_true', help='Test without actual deployment')
    push_parser.add_argument('--skip-backup', action='store_true', help='Skip pre-deployment backup')
    push_parser.add_argument('--skip-verify', action='store_true', help='Skip post-deployment verification')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull data from server')
    pull_parser.add_argument('what', choices=['logs', 'backups', 'configs'], help='What to pull')
    pull_parser.add_argument('--output', '-o', help='Output directory')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check system status on server')
    status_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed status')
    
    # Execute command
    exec_parser = subparsers.add_parser('exec', help='Execute command on server')
    exec_parser.add_argument('exec_command', help='Command to execute')
    exec_parser.add_argument('--timeout', '-t', type=int, default=120, help='Timeout in seconds')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to previous release')
    rollback_parser.add_argument('--list', action='store_true', help='List available releases')
    rollback_parser.add_argument('--release', '-r', help='Specific release to rollback to')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test connection and configuration')
    
    args = parser.parse_args()
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Execute command
    try:
        if args.command == 'init':
            from bridge_tool.commands.init import run_init
            run_init()
        
        elif args.command == 'push':
            from bridge_tool.commands.push import run_push
            run_push(dry_run=args.dry_run, skip_backup=args.skip_backup, skip_verify=args.skip_verify)
        
        elif args.command == 'pull':
            from bridge_tool.commands.pull import run_pull
            run_pull(what=args.what, output=args.output)
        
        elif args.command == 'status':
            from bridge_tool.commands.status import run_status
            run_status(detailed=args.detailed)
        
        elif args.command == 'exec':
            from bridge_tool.commands.execute import run_execute
            run_execute(command=args.exec_command, timeout=args.timeout)
        
        elif args.command == 'rollback':
            from bridge_tool.commands.rollback import run_rollback
            run_rollback(list_releases=args.list, release=args.release)
        
        elif args.command == 'test':
            from bridge_tool.commands.test import run_test
            run_test()
        
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
