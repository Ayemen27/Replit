#!/usr/bin/env python3
"""
Secrets Management CLI Tool

Provides command-line interface for managing API tokens and secrets securely.
Supports key rotation, token generation, and secret retrieval.
"""
import argparse
import sys
import secrets as py_secrets
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dev_platform.core.secrets_manager import get_secrets_manager


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    return py_secrets.token_urlsafe(length)


def cmd_get(args):
    """Get a secret value"""
    secrets_mgr = get_secrets_manager()
    value = secrets_mgr.get(args.key)
    
    if value:
        if args.show:
            print(f"{args.key}: {value}")
        else:
            print(value)
    else:
        print(f"Error: Secret '{args.key}' not found", file=sys.stderr)
        sys.exit(1)


def cmd_set(args):
    """Set a secret value"""
    secrets_mgr = get_secrets_manager()
    
    if args.generate:
        value = generate_secure_token(args.length)
        print(f"Generated secure token (length={args.length})")
        if args.show:
            print(f"Value: {value}")
    else:
        value = args.value
        if not value:
            print("Error: Either provide a value or use --generate", file=sys.stderr)
            sys.exit(1)
    
    secrets_mgr.set(args.key, value, encrypt=args.encrypt)
    
    location = "encrypted storage" if args.encrypt else ".env file"
    print(f"✓ Secret '{args.key}' saved to {location}")


def cmd_delete(args):
    """Delete a secret"""
    secrets_mgr = get_secrets_manager()
    
    if not args.yes:
        confirm = input(f"Delete secret '{args.key}'? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return
    
    secrets_mgr.delete(args.key)
    print(f"✓ Secret '{args.key}' deleted")


def cmd_list(args):
    """List all secrets"""
    secrets_mgr = get_secrets_manager()
    keys = secrets_mgr.list_keys(encrypted_only=args.encrypted_only)
    
    if not keys:
        print("No secrets found")
        return
    
    print(f"\nFound {len(keys)} secret(s):")
    for key in keys:
        value = secrets_mgr.get(key)
        if args.show and value:
            print(f"  {key}: {value}")
        else:
            masked = "***" if value else "(not set)"
            print(f"  {key}: {masked}")


def cmd_rotate(args):
    """Rotate a secret (generate new value)"""
    secrets_mgr = get_secrets_manager()
    
    old_value = secrets_mgr.get(args.key)
    if not old_value:
        print(f"Error: Secret '{args.key}' not found. Use 'set' to create it.", file=sys.stderr)
        sys.exit(1)
    
    if not args.yes:
        confirm = input(f"Rotate secret '{args.key}'? This will invalidate the old token. [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return
    
    new_value = generate_secure_token(args.length)
    secrets_mgr.set(args.key, new_value, encrypt=True)
    
    print(f"✓ Secret '{args.key}' rotated successfully")
    if args.show:
        print(f"New value: {new_value}")
    else:
        print("New token generated (use --show to display)")


def cmd_dashboard_token(args):
    """Retrieve dashboard API token"""
    secrets_mgr = get_secrets_manager()
    token = secrets_mgr.get("DASHBOARD_API_TOKEN")
    
    if not token:
        print("Dashboard token not found. Generating new one...")
        token = generate_secure_token(32)
        secrets_mgr.set("DASHBOARD_API_TOKEN", token, encrypt=True)
        print("✓ New dashboard token generated and saved")
    
    print(f"\nDashboard API Token:")
    print(f"  {token}")
    print(f"\nTo use with API requests:")
    print(f"  curl -H 'X-API-Token: {token}' http://localhost:5000/api/metrics")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Secrets Management CLI - Secure API key and token management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get dashboard token
  python secrets_cli.py dashboard-token
  
  # Set a secret
  python secrets_cli.py set MY_API_KEY myvalue123
  
  # Generate and set a secure token
  python secrets_cli.py set MY_TOKEN --generate --encrypt
  
  # Rotate an existing token
  python secrets_cli.py rotate DASHBOARD_API_TOKEN
  
  # List all secrets
  python secrets_cli.py list
  
  # Delete a secret
  python secrets_cli.py delete OLD_API_KEY
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    parser_get = subparsers.add_parser('get', help='Get a secret value')
    parser_get.add_argument('key', help='Secret key name')
    parser_get.add_argument('--show', action='store_true', help='Show key name with value')
    parser_get.set_defaults(func=cmd_get)
    
    parser_set = subparsers.add_parser('set', help='Set a secret value')
    parser_set.add_argument('key', help='Secret key name')
    parser_set.add_argument('value', nargs='?', help='Secret value (optional if --generate)')
    parser_set.add_argument('--generate', action='store_true', help='Generate secure random token')
    parser_set.add_argument('--length', type=int, default=32, help='Token length (default: 32)')
    parser_set.add_argument('--encrypt', action='store_true', help='Store in encrypted file instead of .env')
    parser_set.add_argument('--show', action='store_true', help='Display generated value')
    parser_set.set_defaults(func=cmd_set)
    
    parser_delete = subparsers.add_parser('delete', help='Delete a secret')
    parser_delete.add_argument('key', help='Secret key name')
    parser_delete.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')
    parser_delete.set_defaults(func=cmd_delete)
    
    parser_list = subparsers.add_parser('list', help='List all secrets')
    parser_list.add_argument('--show', action='store_true', help='Show values (careful!)')
    parser_list.add_argument('--encrypted-only', action='store_true', help='Show only encrypted secrets')
    parser_list.set_defaults(func=cmd_list)
    
    parser_rotate = subparsers.add_parser('rotate', help='Rotate a secret (generate new value)')
    parser_rotate.add_argument('key', help='Secret key name')
    parser_rotate.add_argument('--length', type=int, default=32, help='New token length (default: 32)')
    parser_rotate.add_argument('--show', action='store_true', help='Display new value')
    parser_rotate.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')
    parser_rotate.set_defaults(func=cmd_rotate)
    
    parser_dashboard = subparsers.add_parser('dashboard-token', help='Get/generate dashboard API token')
    parser_dashboard.set_defaults(func=cmd_dashboard_token)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
