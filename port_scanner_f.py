#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import subprocess
import platform
import time
import sys
from datetime import datetime
import os

# ====== تنظیمات رنگ‌ها برای ترمینال ======
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_banner():
    """نمایش بنر حرفه‌ای"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════╗
║     🔐 Advanced Security Analyzer v2.0          ║
║     {Colors.PURPLE}Ethical Hacking Tool{Colors.CYAN}              ║
╚══════════════════════════════════════════════════╝
{Colors.RESET}
    """
    print(banner)

def get_os_by_ttl(ip):
    """تشخیص سیستمعامل از روی TTL (با پینگ)"""
    try:
        # برای ویندوز
        if platform.system().lower() == 'windows':
            response = subprocess.run(['ping', '-n', '1', ip], capture_output=True, text=True)
        else:
            response = subprocess.run(['ping', '-c', '1', ip], capture_output=True, text=True)
        
        if "TTL=" in response.stdout:
            ttl_line = [line for line in response.stdout.split('\n') if 'TTL=' in line][0]
            ttl = int(ttl_line.split('TTL=')[-1].split()[0])
            
            if ttl <= 64:
                return f"{Colors.GREEN}Linux/Unix{Colors.RESET}"
            elif ttl <= 128:
                return f"{Colors.YELLOW}Windows{Colors.RESET}"
            else:
                return f"{Colors.PURPLE}Unknown{Colors.RESET}"
        return f"{Colors.RED}Unknown{Colors.RESET}"
    except:
        return f"{Colors.RED}Unknown{Colors.RESET}"

def scan_port(ip, port):
    """بررسی باز بودن پورت با timeout 1 ثانیه"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def check_vulnerabilities(ip, open_ports):
    """بررسی آسیب‌پذیری‌های رایج"""
    vulns = []
    
    # چک کردن پورت‌های خطرناک
    dangerous_ports = {
        21: "FTP (بدون رمزنگاری - خطر نشت اطلاعات)",
        22: "SSH (ریسک Brute Force - حتماً کلید SSH بذار)",
        23: "Telnet (کاملاً ناامن - استفاده نکن!)",
        80: "HTTP (بدون SSL - اطلاعات رمز نمی‌شه)",
        3306: "MySQL (احتمال نفوذ به دیتابیس)",
        3389: "RDP (هدف اصلی هکرها برای حمله)",
        5900: "VNC (بدون امنیت - به راحتی هک میشه)"
    }
    
    for port in open_ports:
        if port in dangerous_ports:
            vulns.append(f"⚠️ پورت {port}: {dangerous_ports[port]}")
    
    # تست پسورد پیش‌فرض MySQL (فقط شبیه‌سازی)
    if 3306 in open_ports:
        vulns.append("🔴 خطر: MySQL ممکن است با پسورد پیش‌فرض (root/blank) باشد!")
    
    return vulns

def generate_report(ip, hostname, os_info, open_ports, vulns, scan_time):
    """تولید گزارش متنی زیبا"""
    report = f"""
{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════{Colors.RESET}
{Colors.BOLD}📋 گزارش امنیتی کامل{Colors.RESET}
{Colors.CYAN}═══════════════════════════════════════════════════{Colors.RESET}

🌐 {Colors.BOLD}آدرس هدف:{Colors.RESET} {ip} ({hostname})
🕒 {Colors.BOLD}زمان اسکن:{Colors.RESET} {scan_time}
💻 {Colors.BOLD}سیستم‌عامل تشخیص داده شده:{Colors.RESET} {os_info}

{Colors.BOLD}{Colors.YELLOW}🔍 پورت‌های باز یافت شده:{Colors.RESET}
"""
    if open_ports:
        for port in open_ports:
            report += f"   ✅ پورت {port} باز است\n"
    else:
        report += f"   {Colors.GREEN}✅ هیچ پورت خطری پیدا نشد{Colors.RESET}\n"
    
    if vulns:
        report += f"\n{Colors.BOLD}{Colors.RED}⚠️ آسیب‌پذیری‌های تشخیص داده شده:{Colors.RESET}\n"
        for vuln in vulns:
            report += f"   {vuln}\n"
    else:
        report += f"\n{Colors.GREEN}✅ هیچ آسیب‌پذیری خطرناکی پیدا نشد{Colors.RESET}\n"
    
    report += f"""
{Colors.BOLD}{Colors.GREEN}💡 توصیه‌های امنیتی:{Colors.RESET}
1. همیشه از فایروال استفاده کن.
2. پورت‌های غیرضروری رو ببند.
3. از پسوردهای قوی (حداقل ۱۲ کاراکتر) استفاده کن.
4. سیستم‌عامل و سرویس‌ها رو به‌روز نگه دار.

{Colors.CYAN}═══════════════════════════════════════════════════{Colors.RESET}
{Colors.BOLD}🔐 این گزارش توسط Advanced Security Analyzer تهیه شده است.{Colors.RESET}
"""
    return report

def save_report_to_file(report, ip):
    """ذخیره گزارش در فایل"""
    filename = f"security_report_{ip.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n{Colors.GREEN}✅ گزارش در فایل {filename} ذخیره شد.{Colors.RESET}")
        return filename
    except:
        print(f"{Colors.RED}❌ خطا در ذخیره‌سازی فایل{Colors.RESET}")
        return None

def main():
    print_banner()
    
    # گرفتن آدرس از کاربر
    target = input(f"{Colors.YELLOW}🎯 آدرس IP یا دامنه را وارد کن (مثلاً google.com): {Colors.RESET}").strip()
    
    if not target:
        print(f"{Colors.RED}❌ خطا: آدرسی وارد نشد!{Colors.RESET}")
        return
    
    try:
        ip = socket.gethostbyname(target)
        hostname = socket.gethostbyaddr(ip)[0] if target == ip else target
    except:
        print(f"{Colors.RED}❌ خطا: آدرس نامعتبر است!{Colors.RESET}")
        return
    
    scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n{Colors.BLUE}⏳ شروع اسکن بر روی {ip} ...{Colors.RESET}")
    time.sleep(1)
    
    # تشخیص سیستم‌عامل
    print(f"{Colors.BLUE}🔍 در حال تشخیص سیستم‌عامل...{Colors.RESET}")
    os_info = get_os_by_ttl(ip)
    print(f"{Colors.GREEN}✅ سیستم‌عامل: {os_info}{Colors.RESET}")
    
    # لیست پورت‌های مهم
    ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 5900, 8080, 8443]
    
    print(f"\n{Colors.BLUE}🔎 اسکن پورت‌های رایج...{Colors.RESET}")
    open_ports = []
    
    for port in ports_to_scan:
        sys.stdout.write(f"{Colors.CYAN}در حال بررسی پورت {port}...{Colors.RESET} ")
        if scan_port(ip, port):
            print(f"{Colors.GREEN}✅ باز است{Colors.RESET}")
            open_ports.append(port)
        else:
            print(f"{Colors.RED}❌ بسته است{Colors.RESET}")
        time.sleep(0.1)  # جلوگیری از ارور Too Many Requests
    
    # بررسی آسیب‌پذیری‌ها
    print(f"\n{Colors.BLUE}🔐 بررسی آسیب‌پذیری‌ها...{Colors.RESET}")
    vulns = check_vulnerabilities(ip, open_ports)
    
    # تولید گزارش
    report = generate_report(ip, hostname, os_info, open_ports, vulns, scan_time)
    print(report)
    
    # ذخیره گزارش
    save = input(f"{Colors.YELLOW}💾 آیا می‌خواهی گزارش رو ذخیره کنی؟ (y/n): {Colors.RESET}").lower()
    if save == 'y':
        save_report_to_file(report, ip)
    
    print(f"\n{Colors.GREEN}✅ اسکن با موفقیت به پایان رسید!{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}⛔ اسکن توسط کاربر متوقف شد.{Colors.RESET}")
        sys.exit(0)