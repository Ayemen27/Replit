"""Push/Deploy command with GitHub integration"""

import os
import json
from datetime import datetime
from pathlib import Path
from bridge_tool.config_loader import ConfigLoader
from bridge_tool.services.ssh_client import SSHClientManager
from bridge_tool.services.sync_manager import SyncManager
from bridge_tool.services.git_manager import GitManager


def _save_deployment_report(report_data: dict, report_path: str):
    """Save deployment report"""
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_path = report_path.replace('.md', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    # Save Markdown
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 📋 تقرير النشر (Deployment Report)\n\n")
        f.write(f"**التاريخ (Date):** {report_data.get('timestamp', 'N/A')}\n")
        f.write(f"**الحالة (Status):** {'✓ نجح (Success)' if report_data.get('success') else '✗ فشل (Failed)'}\n\n")
        
        f.write("## معلومات Git (Git Information)\n\n")
        git_info = report_data.get('git', {})
        f.write(f"- **الفرع (Branch):** {git_info.get('branch', 'N/A')}\n")
        f.write(f"- **الإصدار (Tag):** {git_info.get('tag', 'N/A')}\n")
        f.write(f"- **Commit Hash:** {git_info.get('commit', 'N/A')}\n")
        f.write(f"- **المستودع (Repository):** {git_info.get('repository', 'N/A')}\n\n")
        
        f.write("## معلومات السيرفر (Server Information)\n\n")
        server_info = report_data.get('server', {})
        f.write(f"- **Host:** {server_info.get('host', 'N/A')}\n")
        f.write(f"- **مسار النشر (Release Path):** {server_info.get('release_path', 'N/A')}\n")
        f.write(f"- **الملفات المنقولة (Files Transferred):** {server_info.get('files_transferred', 0)}\n\n")
        
        if report_data.get('errors'):
            f.write("## الأخطاء (Errors)\n\n")
            for error in report_data.get('errors', []):
                f.write(f"- {error}\n")


def run_push(dry_run=False, skip_backup=False, skip_verify=False):
    """
    Deploy to production server via GitHub
    
    Workflow: Replit → GitHub → Server
    
    Args:
        dry_run: Test without actual deployment
        skip_backup: Skip pre-deployment backup
        skip_verify: Skip post-deployment verification
    """
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'success': False,
        'git': {},
        'server': {},
        'errors': []
    }
    
    print("="* 60)
    print(f"{'[DRY RUN] ' if dry_run else ''}Bridge Tool - النشر عبر GitHub")
    print("="* 60)
    
    # Load configuration
    print("\n1️⃣  تحميل الإعدادات (Loading configuration)...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        print("✓ تم تحميل الإعدادات")
    except Exception as e:
        print(f"✗ فشل تحميل الإعدادات: {e}")
        report_data['errors'].append(f"Config load failed: {e}")
        return False
    
    git_config = config.get('git', {})
    server_config = config.get('server', {})
    paths_config = config.get('paths', {})
    deployment_config = config.get('deployment', {})
    
    strategy = git_config.get('strategy', 'github_first')
    
    # Check if GitHub strategy is enabled
    if strategy != 'github_first':
        print(f"\n⚠️  استراتيجية النشر الحالية: {strategy}")
        print("للنشر عبر GitHub، قم بتعيين git.strategy = 'github_first' في bridge.config.yaml")
        print("النشر عبر GitHub معطل. يرجى تعيين git.strategy = 'github_first'\n")
        report_data['errors'].append("GitHub strategy not enabled")
        return False
    
    # Initialize Git Manager
    print("\n2️⃣  تهيئة Git Manager...")
    try:
        git_manager = GitManager(git_config, paths_config.get('local', {}).get('root', '.'))
        
        if not git_manager.check_git_available():
            raise Exception("Git غير متوفر في النظام")
        
        if not git_manager.is_git_repository():
            raise Exception("المجلد الحالي ليس مستودع Git")
        
        print("✓ Git Manager جاهز")
        
    except Exception as e:
        print(f"✗ فشل تهيئة Git: {e}")
        report_data['errors'].append(f"Git init failed: {e}")
        return False
    
    # Run Git workflow: commit → tag → push to GitHub
    print("\n3️⃣  تنفيذ عملية Git (Git workflow)...")
    success, git_metadata = git_manager.full_deployment_workflow(dry_run=dry_run)
    
    if not success:
        print("✗ فشلت عملية Git")
        report_data['errors'].append("Git workflow failed")
        return False
    
    report_data['git'] = git_metadata
    report_data['git']['repository'] = git_config.get('repository', '')
    
    print("✓ تم رفع التحديثات إلى GitHub بنجاح")
    
    # Create timestamped release directory
    release_tag = git_metadata.get('tag', '')
    release_name = release_tag or f"release_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    releases_path = paths_config.get('remote', {}).get('releases', '/srv/ai_system/releases')
    current_path = paths_config.get('remote', {}).get('current', '/srv/ai_system/current')
    release_path = f"{releases_path}/{release_name}"
    
    report_data['server']['host'] = server_config.get('host', '')
    report_data['server']['release_path'] = release_path
    
    # Connect to server
    print(f"\n4️⃣  الاتصال بالسيرفر (Connecting to server)...")
    with SSHClientManager(server_config) as ssh:
        if not ssh.client:
            print("✗ فشل الاتصال بالسيرفر")
            report_data['errors'].append("SSH connection failed")
            _save_deployment_report(report_data, f"bridge_reports/deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            return False
        
        print("✓ تم الاتصال بالسيرفر")
        
        # Create release directory
        print(f"\n5️⃣  إنشاء مجلد الإصدار (Creating release directory)...")
        if not dry_run:
            ssh.create_directory(release_path)
            print(f"✓ تم إنشاء: {release_path}")
        else:
            print(f"[DRY RUN] سيتم إنشاء: {release_path}")
        
        # Backup if needed
        if not skip_backup and not dry_run:
            print(f"\n6️⃣  إنشاء نسخة احتياطية (Creating backup)...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = paths_config.get('remote', {}).get('backups', '/srv/ai_system/backups')
            backup_commands = [
                f"mkdir -p {backup_path}/pre_deploy_{timestamp}",
                f"cp -r {current_path}/configs {backup_path}/pre_deploy_{timestamp}/ 2>/dev/null || true",
                f"cp -r {current_path}/logs {backup_path}/pre_deploy_{timestamp}/ 2>/dev/null || true",
                f"cp -r {current_path}/data {backup_path}/pre_deploy_{timestamp}/ 2>/dev/null || true"
            ]
            ssh.execute_commands(backup_commands, stop_on_error=False)
            print("✓ تم إنشاء النسخة الاحتياطية")
        
        # Clone/Pull from GitHub on server
        step = 6 if skip_backup else 7
        print(f"\n{step}️⃣  سحب الكود من GitHub إلى السيرفر...")
        
        repo_url = f"https://github.com/{git_config.get('repository', '')}.git"
        
        # Check if git is available on server
        exit_code, _, _ = ssh.execute_command('which git')
        if exit_code != 0:
            print("⚠️  Git غير متوفر على السيرفر، سيتم النشر عبر SFTP...")
            
            # Fallback to sync files
            sync_manager = SyncManager(ssh, config)
            if config.get('sync', {}).get('prefer_rsync', False):
                if not sync_manager.sync_directory_rsync(release_path, dry_run):
                    total, transferred, errors = sync_manager.sync_files(release_path, dry_run)
                    report_data['server']['files_transferred'] = transferred
                    if errors:
                        report_data['errors'].extend(errors[:5])
            else:
                total, transferred, errors = sync_manager.sync_files(release_path, dry_run)
                report_data['server']['files_transferred'] = transferred
                if errors:
                    report_data['errors'].extend(errors[:5])
        else:
            # Clone from GitHub
            if not dry_run:
                clone_cmd = f"""
                if [ -d {release_path}/.git ]; then
                    cd {release_path} && git fetch --all --tags && git checkout {release_tag}
                else
                    git clone --depth 1 --branch {git_metadata.get('branch', 'main')} {repo_url} {release_path} && cd {release_path} && git checkout {release_tag}
                fi
                """
                
                exit_code, stdout, stderr = ssh.execute_command(clone_cmd, timeout=300)
                
                if exit_code == 0:
                    print(f"✓ تم سحب الكود من GitHub (Tag: {release_tag})")
                else:
                    print(f"✗ فشل سحب الكود من GitHub: {stderr}")
                    report_data['errors'].append(f"Git clone failed: {stderr}")
                    _save_deployment_report(report_data, f"bridge_reports/deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
                    return False
            else:
                print(f"[DRY RUN] سيتم سحب الكود من {repo_url} (Tag: {release_tag})")
        
        # Run post-deployment scripts
        if not dry_run:
            step += 1
            print(f"\n{step}️⃣  تنفيذ سكربتات ما بعد النشر...")
            post_scripts = deployment_config.get('scripts', {}).get('post_deploy', [])
            
            for script in post_scripts:
                script_name = script.get('name', 'Unknown')
                script_cmd = script.get('command', '')
                
                if script_cmd:
                    print(f"  ▶️  {script_name}...")
                    exit_code, stdout, stderr = ssh.execute_command(f"cd {release_path} && {script_cmd}")
                    
                    if exit_code == 0:
                        print(f"  ✓ {script_name}")
                    else:
                        print(f"  ✗ {script_name} - {stderr[:100]}")
                        report_data['errors'].append(f"{script_name} failed: {stderr[:100]}")
            
            # Update symlink to current release
            step += 1
            print(f"\n{step}️⃣  تحديث الرابط الرمزي (Updating symlink)...")
            symlink_commands = [
                f"rm -f {current_path}",
                f"ln -s {release_path} {current_path}"
            ]
            ssh.execute_commands(symlink_commands)
            print("✓ تم تحديث current → " + release_path)
            
            # Cleanup old releases
            keep_releases = deployment_config.get('keep_releases', 5)
            step += 1
            print(f"\n{step}️⃣  تنظيف الإصدارات القديمة (Cleanup)...")
            cleanup_cmd = f"""
            cd {releases_path} && ls -t | tail -n +{keep_releases + 1} | xargs -r rm -rf
            """
            ssh.execute_command(cleanup_cmd)
            print(f"✓ تم الاحتفاظ بآخر {keep_releases} إصدارات")
            
            # Verify deployment
            if not skip_verify:
                step += 1
                print(f"\n{step}️⃣  التحقق من النشر (Verification)...")
                verify_cmd = f"cd {current_path} && python3 main.py status"
                exit_code, stdout, stderr = ssh.execute_command(verify_cmd, timeout=30)
                
                if exit_code == 0:
                    print("✓ تم التحقق من النشر بنجاح")
                else:
                    print("⚠️  فشل التحقق من النشر")
                    report_data['errors'].append("Deployment verification failed")
        
        print("\n" + "="* 60)
        if dry_run:
            print("اكتمل اختبار النشر - لم يتم إجراء أي تغييرات فعلية")
            print("DRY RUN COMPLETE - No actual changes made")
        else:
            print("✅ اكتمل النشر بنجاح (DEPLOYMENT SUCCESSFUL)")
            print(f"📌 الإصدار (Release): {release_name}")
            print(f"🏷️  Tag: {release_tag}")
            print(f"📝 Commit: {git_metadata.get('commit', 'N/A')}")
            print(f"🌿 Branch: {git_metadata.get('branch', 'N/A')}")
            print(f"📂 المسار (Path): {release_path}")
            
            report_data['success'] = True
            
            # Save deployment report
            report_path = f"bridge_reports/deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            _save_deployment_report(report_data, report_path)
            print(f"\n📋 تم حفظ التقرير: {report_path}")
        
        print("="* 60)
        
        return True
