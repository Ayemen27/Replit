"""Rollback to previous release (supports Git tags)"""

from bridge_tool.config_loader import ConfigLoader
from bridge_tool.services.ssh_client import SSHClientManager
from bridge_tool.services.git_manager import GitManager


def run_rollback(list_releases=False, release=None):
    """
    Rollback to previous release
    
    Supports both directory-based and Git tag-based rollbacks
    
    Args:
        list_releases: List available releases
        release: Specific release to rollback to
    """
    
    print("="* 60)
    print("Bridge Tool - التراجع إلى إصدار سابق (Rollback)")
    print("="* 60)
    
    # Load configuration
    print("\n1️⃣  تحميل الإعدادات (Loading configuration)...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        print("✓ تم تحميل الإعدادات")
    except Exception as e:
        print(f"✗ فشل تحميل الإعدادات: {e}")
        return False
    
    git_config = config.get('git', {})
    strategy = git_config.get('strategy', 'direct')
    
    # Connect to server
    print("\n2️⃣  الاتصال بالسيرفر (Connecting to server)...")
    with SSHClientManager(config.get('server', {})) as ssh:
        if not ssh.client:
            print("✗ فشل الاتصال بالسيرفر")
            return False
        
        print("✓ تم الاتصال بالسيرفر")
        
        releases_path = config.get('paths', {}).get('remote', {}).get('releases', '/srv/ai_system/releases')
        current_path = config.get('paths', {}).get('remote', {}).get('current', '/srv/ai_system/current')
        service_name = config.get('deployment', {}).get('service_name', 'ai_agents')
        
        # Check if using Git-based deployment by checking releases directory
        # Each release should have its own .git if using GitHub strategy
        exit_code, stdout, _ = ssh.execute_command(f'ls -d {releases_path}/release_*/.git 2>/dev/null | head -1')
        uses_git = exit_code == 0 and stdout.strip()
        
        if uses_git or strategy == 'github_first':
            print("\n📋 استخدام Git لإدارة الإصدارات")
            return _rollback_git_based(ssh, config, list_releases, release)
        else:
            print("\n📋 استخدام المجلدات لإدارة الإصدارات")
            return _rollback_directory_based(ssh, config, list_releases, release)


def _rollback_git_based(ssh, config, list_releases, release):
    """Rollback using Git tags from release directories"""
    
    releases_path = config.get('paths', {}).get('remote', {}).get('releases', '/srv/ai_system/releases')
    current_path = config.get('paths', {}).get('remote', {}).get('current', '/srv/ai_system/current')
    service_name = config.get('deployment', {}).get('service_name', 'ai_agents')
    
    print("\n3️⃣  جلب قائمة الإصدارات...")
    
    # List release directories (they ARE the tags)
    exit_code, stdout, _ = ssh.execute_command(f'ls -1t {releases_path}')
    
    if exit_code != 0 or not stdout.strip():
        print("✗ لم يتم العثور على إصدارات")
        return False
    
    releases = stdout.strip().split('\n')
    tags = [r.strip() for r in releases if r.strip().startswith('release_')]
    
    if not tags:
        print("✗ لم يتم العثور على إصدارات Git")
        return False
    
    # Get current release
    exit_code, current_release, _ = ssh.execute_command(f'readlink {current_path}')
    current_tag = current_release.strip().split('/')[-1] if exit_code == 0 else 'unknown'
    
    print(f"\n✅ الإصدار الحالي (Current): {current_tag}")
    print(f"\n📋 الإصدارات المتاحة ({len(tags)}):")
    for i, tag in enumerate(tags, 1):
        marker = " ← الحالي (CURRENT)" if tag.strip() == current_tag else ""
        print(f"  {i}. {tag.strip()}{marker}")
    
    if list_releases:
        return True
    
    # Select release for rollback
    if not release:
        if len(tags) < 2:
            print("\n✗ لا يوجد إصدار سابق متاح للتراجع")
            return False
        
        # Use the second tag (previous one)
        release = tags[1].strip()
        print(f"\n⏪ التراجع إلى (Rolling back to): {release}")
    else:
        if release not in [t.strip() for t in tags]:
            print(f"\n✗ الإصدار '{release}' غير موجود")
            return False
        print(f"\n⏪ التراجع إلى: {release}")
    
    # Confirm rollback
    response = input("\n⚠️  هل أنت متأكد من التراجع؟ (y/N): ")
    if response.lower() != 'y':
        print("تم إلغاء التراجع (Rollback cancelled)")
        return False
    
    # Perform rollback by updating symlink
    print("\n4️⃣  تنفيذ التراجع (Performing rollback)...")
    
    release_path = f"{releases_path}/{release}"
    
    rollback_commands = [
        # Stop service
        f"systemctl stop {service_name} 2>/dev/null || true",
        
        # Update symlink to point to the selected release
        f"rm -f {current_path}",
        f"ln -s {release_path} {current_path}",
        
        # Reinstall dependencies if needed
        f"cd {current_path} && pip3 install -r requirements.txt 2>/dev/null || true",
        
        # Restart service
        f"systemctl start {service_name} 2>/dev/null || true"
    ]
    
    results = ssh.execute_commands(rollback_commands, stop_on_error=False)
    
    # Verify rollback
    print("\n5️⃣  التحقق من التراجع (Verifying rollback)...")
    exit_code, new_current, _ = ssh.execute_command(f'readlink {current_path}')
    
    if exit_code == 0 and release in new_current:
        print(f"✅ تم التراجع بنجاح (Rollback successful)")
        print(f"الإصدار الحالي (Current): {new_current.strip()}")
        
        # Check service status
        exit_code, status, _ = ssh.execute_command(f'systemctl is-active {service_name} 2>&1 || echo "manual"')
        if 'active' in status.lower():
            print(f"✅ الخدمة تعمل (Service is active)")
        else:
            print(f"⚠️  حالة الخدمة: {status.strip()}")
            print("قد تحتاج إلى تشغيل الخدمة يدوياً")
        
        return True
    else:
        print(f"✗ فشل التحقق من التراجع")
        return False


def _rollback_directory_based(ssh, config, list_releases, release):
    """Rollback using release directories"""
    
    releases_path = config.get('paths', {}).get('remote', {}).get('releases', '/srv/ai_system/releases')
    current_path = config.get('paths', {}).get('remote', {}).get('current', '/srv/ai_system/current')
    service_name = config.get('deployment', {}).get('service_name', 'ai_agents')
    
    # List available releases
    print("\n3️⃣  جلب قائمة الإصدارات...")
    exit_code, stdout, _ = ssh.execute_command(f'ls -1t {releases_path}')
    
    if exit_code != 0 or not stdout.strip():
        print("✗ لم يتم العثور على إصدارات")
        return False
    
    releases = stdout.strip().split('\n')
    
    # Get current release
    exit_code, current_release, _ = ssh.execute_command(f'readlink {current_path}')
    current_release = current_release.strip() if exit_code == 0 else 'unknown'
    
    print(f"\n✅ الإصدار الحالي: {current_release}")
    print(f"\n📋 الإصدارات المتاحة ({len(releases)}):")
    for i, rel in enumerate(releases, 1):
        marker = " ← الحالي" if rel.strip() in current_release else ""
        print(f"  {i}. {rel.strip()}{marker}")
    
    if list_releases:
        return True
    
    # Select release for rollback
    if not release:
        if len(releases) < 2:
            print("\n✗ لا يوجد إصدار سابق متاح للتراجع")
            return False
        
        # Use the second release (previous one)
        release = releases[1].strip()
        print(f"\n⏪ التراجع إلى: {release}")
    else:
        if release not in [r.strip() for r in releases]:
            print(f"\n✗ الإصدار '{release}' غير موجود")
            return False
        print(f"\n⏪ التراجع إلى: {release}")
    
    # Confirm rollback
    response = input("\n⚠️  هل أنت متأكد من التراجع؟ (y/N): ")
    if response.lower() != 'y':
        print("تم إلغاء التراجع")
        return False
    
    # Perform rollback
    print("\n4️⃣  تنفيذ التراجع...")
    
    release_path = f"{releases_path}/{release}"
    
    rollback_commands = [
        # Stop service
        f"systemctl stop {service_name} 2>/dev/null || true",
        
        # Update symlink
        f"rm -f {current_path}",
        f"ln -s {release_path} {current_path}",
        
        # Restart service
        f"systemctl start {service_name} 2>/dev/null || true"
    ]
    
    results = ssh.execute_commands(rollback_commands, stop_on_error=False)
    
    # Verify rollback
    print("\n5️⃣  التحقق من التراجع...")
    exit_code, new_current, _ = ssh.execute_command(f'readlink {current_path}')
    
    if exit_code == 0 and release in new_current:
        print(f"✅ تم التراجع بنجاح")
        print(f"الإصدار الحالي: {new_current.strip()}")
        
        # Check service status
        exit_code, status, _ = ssh.execute_command(f'systemctl is-active {service_name} 2>&1 || echo "manual"')
        if 'active' in status.lower():
            print(f"✅ الخدمة تعمل")
        else:
            print(f"⚠️  حالة الخدمة: {status.strip()}")
            print("قد تحتاج إلى تشغيل الخدمة يدوياً")
        
        return True
    else:
        print(f"✗ فشل التحقق من التراجع")
        return False
