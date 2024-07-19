import os
from rich.console import Console

console = Console()
import requests
import json
from noneprompt import ListPrompt, Choice, InputPrompt, CancelledError
import sys
from time import sleep, time
import random
import sqlite3
import shutil
import zipfile

ADB_PATH = "bin\\adb.exe"
FASTBOOT_PATH = "bin\\fastboot.exe"
SPD_DUMP_PATH = "bin\\spd_dump.exe"


class Tool:

    def __init__(self):
        url = "https://v1.hitokoto.cn/?c=i"
        res = requests.get(url)
        self.hitokoto_data = json.loads(res.text)

    def root(self):
        console.print(
            "[bold red][WARNING] Root手表可能会使您的手表变砖并清除所有数据,如出现任何问题，作者概不负责！！！"
        )
        get_list = ListPrompt(
            "请确认刷机方案:",
            choices=[Choice("FastBoot刷机"), Choice("Autodloader刷机")],
        ).prompt()
        get_list_data = ListPrompt(
            "请确认刷机方案:", choices=[Choice("保留数据"), Choice("不保留数据")]
        ).prompt()
        confirm = InputPrompt(
            "请输入yes以确认是否开始刷机", validator=lambda string: True
        ).prompt()
        if confirm == "yes":
            with console.status("[bold green][INFO] 5秒后开始刷机......"):
                sleep(5)
            if get_list.name == "FastBoot刷机":
                console.print("[bold green][INFO] 正在重启设备到FastBoot模式......")
                os.system(f"{ADB_PATH} reboot bootloader")
                console.print("[bold green][INFO] 刷入Boot镜像......")
                os.system(
                    f"{FASTBOOT_PATH} flash boot firmware\\boot.img | bin\\lolcat"
                )
                if get_list_data.name == "不保留数据":
                    console.print("[bold green][INFO] 刷入UserData镜像......")
                    os.system(
                        f"{FASTBOOT_PATH} flash userdata firmware\\userdata.img | bin\\lolcat"
                    )
                    console.print("[bold green][INFO] 重启设备......")
                    os.system(f"{FASTBOOT_PATH} reboot | bin\\lolcat")
                    console.print(
                        "[bold green][INFO] 刷入完成，请等待设备开机后使用*#0769651#*打开ADB后重启手表,等待设备开机后按任意键......"
                    )
                elif get_list_data.name == "保留数据":
                    console.print("[bold green][INFO] 重启设备......")
                    os.system(f"{FASTBOOT_PATH} reboot | bin\\lolcat")
                    console.print(
                        "[bold green][INFO] 刷入完成，请等待设备开机后按任意键......"
                    )
                InputPrompt("请按回车键继续/回到主页面").prompt()
                if get_list_data.name == "保留数据":
                    os.system(f"{ADB_PATH} wait-for-device")
                    console.print("[bold green][INFO] 正在安装Magisk管理器......")
                    os.system(
                        f"{ADB_PATH} wait-for-device install firmware\\magisk.apk"
                    )
                    console.print("[bold green][INFO] 正在安装ES文件管理器......")
                    os.system(
                        f"{ADB_PATH} wait-for-device install firmware\\ES_File.apk"
                    )
                    os.system(f"{ADB_PATH} wait-for-device shell wm density 150")
                    console.print(
                        "[bold green][INFO] 请去Magisk管理器内启用自动响应并将超级用户通知改为无后再按任意键......"
                    )
                    InputPrompt("请按回车键继续/回到主页面").prompt()
                    self.fix_env(go_home=False)

            elif get_list.name == "Autodloader刷机":
                console.print("[bold green][INFO] 正在重启设备到Autodloader模式......")
                os.system(f"{ADB_PATH} reboot autodloader")
                console.print("[bold green][INFO] 启动spd_dump开始刷机......")
                if get_list_data.name == "保留数据":
                    os.system(
                        f"{SPD_DUMP_PATH} fdl firmware\\fdl1-sign.bin 0x5000 fdl firmware\\fdl2-sign.bin 0x9efffe00 skip_confirm 1 exec write_part boot firmware\\boot.img write_part uboot firmware\\u-boot-sign.bin write_part splloader firmware\\u-boot-spl-16k-sign.bin repartition firmware\\sp9820e_xtc_i28.xml reset"
                    )
                elif get_list_data.name == "不保留数据":
                    os.system(
                        f"{SPD_DUMP_PATH} fdl firmware\\fdl1-sign.bin 0x5000 fdl firmware\\fdl2-sign.bin 0x9efffe00 skip_confirm 1 exec write_part boot firmware\\boot.img write_part userdata firmware\\userdata.img write_part uboot firmware\\u-boot-sign.bin write_part splloader firmware\\u-boot-spl-16k-sign.bin repartition firmware\\sp9820e_xtc_i28.xml reset"
                    )
                console.print(
                    "[bold green][INFO] 刷入完成，请等待设备开机后按任意键......"
                )
                InputPrompt("请按回车键继续/回到主页面").prompt()
                if get_list_data.name == "保留数据":
                    os.system(f"{ADB_PATH} wait-for-device")
                    console.print("[bold green][INFO] 正在安装Magisk管理器......")
                    os.system(
                        f"{ADB_PATH} wait-for-device install firmware\\magisk.apk"
                    )
                    console.print("[bold green][INFO] 正在安装ES文件管理器......")
                    os.system(
                        f"{ADB_PATH} wait-for-device install firmware\\ES_File.apk"
                    )
                    os.system(f"{ADB_PATH} wait-for-device shell wm density 150")
                    console.print(
                        "[bold green][INFO] 请去Magisk管理器内启用自动响应并将超级用户通知改为无后再按任意键......"
                    )
                    InputPrompt("请按回车键继续/回到主页面").prompt()
                    os.system(f"{ADB_PATH} shell wm density reset")
                    self.fix_env(go_home=False)
        else:
            self.splash_screen()
        InputPrompt("请按回车键继续/回到主页面").prompt()
        os.system(f"{ADB_PATH} shell wm density reset")
        console.print("[bold green][INFO] 正在准备安装XTCModule")
        console.print("[bold green][INFO] 正在推送XTCModule进入设备")
        os.system(
            f"{ADB_PATH} wait-for-device push firmware\\xtcmodule.zip /sdcard/xtcme.zip"
        )
        console.print("[bold green][INFO] 正在推送XTCModule安装脚本进入设备")
        os.system(
            f"{ADB_PATH} wait-for-device push scripts\\xtcmodule.sh /sdcard/xtcmodule.sh"
        )
        os.system(
            f'{ADB_PATH} wait-for-device shell su -c "chmod 777 /sdcard/xtcmodule.sh"'
        )
        console.print("[bold green][INFO] 开始安装模块")
        os.system(f'{ADB_PATH} wait-for-device shell su -c "sh /sdcard/xtcmodule.sh"')
        os.system(f"{ADB_PATH} shell wm density reset")
        console.print("[bold green][INFO] 重启设备......")
        os.system(f"{ADB_PATH} wait-for-device reboot")
        console.print("[bold green][INFO] 等待检测XTCModule安装状态......")
        os.system(f"{ADB_PATH} wait-for-device")
        sleep(1)
        if "userdebug" in os.popen(f"{ADB_PATH} shell getprop ro.build.type").read():
            console.print("[bold green][INFO] XTCModule正常工作中")
        else:
            console.print(
                "[bold red][ERROR] XTCModule安装失败!请尝试手动使用管理器刷入根目录下的xtcme.zip!"
            )
        InputPrompt("请按回车键继续/回到主页面").prompt()
        self.splash_screen()

    def installapps(self):
        apk_path = InputPrompt("请拖入应用apk:", validator=lambda string: True).prompt()
        os.system(f"{ADB_PATH} push {apk_path} /sdcard/temp.apk")
        os.system(f"{ADB_PATH} shell pm install -r /sdcard/temp.apk")
        os.system(f"{ADB_PATH} shell rm /sdcard/temp.apk")
        console.print("[green][INFO] 安装完成,请按任意键回到主页面[/green]")
        InputPrompt("请按回车键继续/回到主页面").prompt()
        self.splash_screen()

    def flash_license(self):
        args_list = [
            "ilink_device_id",
            "ilink_device_signature",
            "ilink_key_version",
            "ilink_product_id",
            "ilink_support",
        ]
        get_args = {}
        new_id = {}
        console.print("[bold green][INFO] 正在提取数据库文件......")
        os.mkdir("temp")
        os.system(
            f'{ADB_PATH} shell su -c "cp /data/data/com.android.providers.settings/databases/settings.db /sdcard/settings.db"'
        )
        os.system(f"{ADB_PATH} pull /sdcard/settings.db temp/settings.db")
        db = sqlite3.connect(f"{os.getcwd()}\\temp\\settings.db")
        dbu = db.cursor()
        for text in args_list:
            get_args[text] = console.input(f"[bold green]? [/] [green]{text}数据?:[/] ")
        with console.status("[bold green]正在随机生成id..."):
            new_id["ilink_device_id"] = random.randint(10000, 20000)
            new_id["ilink_device_signature"] = random.randint(20000, 30000)
            new_id["ilink_key_version"] = random.randint(40000, 50000)
            new_id["ilink_product_id"] = random.randint(60000, 70000)
            new_id["ilink_support"] = random.randint(80000, 90000)
        console.print("[bold green][INFO] 开始写入文件")
        for text in args_list:
            dbu.execute(
                f"INSERT INTO global (_id,name,value) VALUES ('{new_id[text]}','{text}','{get_args[text]}');"
            )
        db.commit()
        db.close()
        console.print("[bold green][INFO] 写入文件完成,即将传输至手表")
        os.system(
            f"{ADB_PATH} push {os.getcwd()}\\temp\\settings.db /sdcard/settings.db"
        )
        os.system(
            f'{ADB_PATH} shell su -c "cp /sdcard/settings.db /data/data/com.android.providers.settings/databases/settings.db"'
        )
        console.print("[bold green][INFO] 传输完成,重启手表")
        os.system(f"{ADB_PATH} reboot")
        shutil.rmtree("temp")
        InputPrompt("请按回车键继续/回到主页面").prompt()
        self.splash_screen()

    def backup_restore_modem(self):
        console.print(
            "[bold red][WARNING] 刷机可能会使您的手表变砖并清除所有数据,如出现任何问题，作者概不负责！！！"
        )
        get_list = ListPrompt(
            "请选择操作:", choices=[Choice("备份"), Choice("恢复")]
        ).prompt()
        if get_list.name == "备份":
            console.print("[bold green][INFO] 第一次备份必须使用spd_dump备份!")
            confirm = InputPrompt(
                "请输入yes以确认是否开始刷机", validator=lambda string: True
            ).prompt()
            if confirm != "yes":
                self.splash_screen()
            console.print("[bold green][INFO] 正在重启设备到Autodloader模式......")
            os.system(f"{ADB_PATH} reboot autodloader")
            console.print("[bold green][INFO] 正在启动spd_dump开始刷机......")
            if os.path.exists("modem") != True:
                os.mkdir("modem")
            file_name = f"backup_{time()}.zip"
            os.system(
                f"{SPD_DUMP_PATH} fdl firmware\\fdl1-sign.bin 0x5000 fdl firmware\\fdl2-sign.bin 0x9efffe00 skip_confirm 1 exec read_part prodnv 0 5M modem\\prodnv.bin read_part miscdata 0 1M modem\\miscdata.bin read_part l_fixnv1 0 1M modem\\nv.bin write_part uboot firmware\\u-boot-sign.bin write_part splloader firmware\\u-boot-spl-16k-sign.bin reset"
            )
            zip = zipfile.ZipFile(file_name, "w", zipfile.ZIP_DEFLATED)
            for item in os.listdir("modem"):
                zip.write("modem" + os.sep + item)
            zip.close()
            console.print(f"[bold green][INFO] 备份成功!文件名为{file_name}")
            os.startfile(os.getcwd())
            shutil.rmtree("modem")
            InputPrompt("请按回车键继续/回到主页面").prompt()
            self.splash_screen()
        elif get_list.name == "恢复":
            get1_list = ListPrompt(
                "请选择刷机方案:",
                choices=[Choice("FastBoot刷机"), Choice("Autodloader刷机")],
            ).prompt()
            zip_path = InputPrompt(
                "请拖入备份压缩包:", validator=lambda string: True
            ).prompt()
            zip_file = zipfile.ZipFile(zip_path)
            zip_extract = zip_file.extractall(os.getcwd())
            zip_file.close()
            if get1_list.name == "FastBoot刷机":
                console.print("[bold green][INFO] 正在重启设备到Fastboot模式......")
                os.system(f"{ADB_PATH} reboot bootloader")
                console.print("[bold green][INFO] 刷入prodnv分区......")
                os.system(f"{FASTBOOT_PATH} flash prodnv modem\\prodnv.bin")
                console.print("[bold green][INFO] 刷入miscdata分区......")
                os.system(f"{FASTBOOT_PATH} flash miscdata modem\\miscdata.bin")
                console.print("[bold green][INFO] 刷入l_fixnv1分区......")
                os.system(f"{FASTBOOT_PATH} flash l_fixnv1 modem\\nv.bin")
                console.print("[bold green][INFO] 重启设备......")
                os.system(f"{FASTBOOT_PATH} reboot")
                console.print("[bold green][INFO] 刷入完成")
                InputPrompt("请按回车键继续/回到主页面").prompt()
                self.splash_screen()
            elif get1_list.name == "Autodloader刷机":
                console.print("[bold green][INFO] 正在重启设备到Autodloader模式......")
                os.system(f"{ADB_PATH} reboot autodloader")
                console.print("[bold green][INFO] 正在启动spd_dump开始刷机......")
                os.system(
                    f"{SPD_DUMP_PATH} fdl firmware\\fdl1-sign.bin 0x5000 fdl firmware\\fdl2-sign.bin 0x9efffe00 skip_confirm 1 exec write_part prodnv modem\\prodnv.bin write_part miscdata modem\\miscdata.bin write_part l_fixnv1 modem\\nv.bin write_part uboot firmware\\u-boot-sign.bin write_part splloader firmware\\u-boot-spl-16k-sign.bin reset"
                )
                console.print("[bold green][INFO] 重启设备......")
                console.print("[bold green][INFO] 刷入完成")
                InputPrompt("请按回车键继续/回到主页面").prompt()
                self.splash_screen()

    def fix_env(self, go_home=True):
        if (
            "No such file"
            in os.popen(
                f'{ADB_PATH} wait-for-device shell su -c "ls /data/adb/magisk/boot_patch.sh"'
            ).read()
        ):
            console.print("[bold green][INFO] 正在修复运行环境......")
            os.system(
                f'{ADB_PATH} wait-for-device shell su -c "rm -R /data/adb/magisk/"'
            )
            os.system(f"{ADB_PATH} wait-for-device push magisk /sdcard/magisk/")
            os.system(
                f'{ADB_PATH} wait-for-device shell su -c "cp -R /sdcard/magisk/ /data/adb/"'
            )
            os.system(
                f'{ADB_PATH} wait-for-device shell su -c "chmod -R 777 /data/adb/magisk/*"'
            )
            os.system(f'{ADB_PATH} wait-for-device shell su -c "ls /data/adb/magisk/"')
            console.print("[bold green][INFO] 完成！正在重启设备......")
            os.system(f"{ADB_PATH} wait-for-device reboot")
            if go_home:
                console.print(
                    "[bold green][INFO] 设备重启成功,请按任意键回到主页面[/bold green]"
                )
                InputPrompt("请按回车键继续/回到主页面").prompt()
                self.splash_screen()
        else:
            console.print(
                "[bold red][WARNING] 运行环境已修复,重复修复可能导致卡第二屏！"
            )
            if go_home:
                console.print("[bold green][INFO] 请按任意键回到主页面[/bold green]")
                InputPrompt("请按回车键继续/回到主页面").prompt()
                self.splash_screen()

    def change_boot_logo(self):
        console.print(
            "[bold red][WARNING] 刷机可能会使您的手表变砖并清除所有数据,如出现任何问题，作者概不负责！！！"
        )
        get_list = ListPrompt(
            "请确认方案:", choices=[Choice("FastBoot刷机"), Choice("Autodloader刷机")]
        ).prompt()
        img_path = InputPrompt(
            "请拖入bmp图片(分辨率240*240)", validator=lambda string: True
        ).prompt()
        if get_list.name == "FastBoot刷机":
            console.print("[bold green][INFO] 正在重启设备到FastBoot模式......")
            os.system(f"{ADB_PATH} reboot bootloader")
            console.print("[bold green][INFO] 正在刷入logo......")
            os.system(f"{FASTBOOT_PATH} flash logo {img_path}")
            console.print("[bold green][INFO] 正在重启设备......")
            os.system(f"{FASTBOOT_PATH} reboot")
            console.print("[bold green][INFO] 刷入完成")
            InputPrompt("请按回车键继续/回到主页面").prompt()
        elif get_list.name == "Autodloader刷机":
            console.print("[bold green][INFO] 正在重启设备到Autodloader模式......")
            os.system(f"{ADB_PATH} reboot autodloader")
            console.print("[bold green][INFO] 正在启动spd_dump开始刷机......")
            os.system(
                f"{SPD_DUMP_PATH} fdl firmware\\fdl1-sign.bin 0x5000 fdl firmware\\fdl2-sign.bin 0x9efffe00 skip_confirm 1 exec write_part logo {img_path} write_part uboot firmware\\u-boot-sign.bin write_part splloader firmware\\u-boot-spl-16k-sign.bin reset"
            )
            console.print("[bold green][INFO] 正在重启设备......")
            console.print("[bold green][INFO] 刷入完成")
            InputPrompt("请按回车键继续/回到主页面").prompt()
        self.splash_screen()

    def change_dpi(self):
        get_input = ListPrompt(
            "请选择操作:", choices=[Choice("修改"), Choice("还原")]
        ).prompt()
        if get_input.name == "修改":
            dpi_value = InputPrompt(
                "请输入更改的DPI数值:", validator=lambda s: s.isdigit()
            ).prompt()
            os.system(f"{ADB_PATH} shell wm density {dpi_value}")
            InputPrompt("更改完成,请按回车键继续/回到主页面").prompt()
            self.splash_screen()
        elif get_input.name == "还原":
            os.system(f"{ADB_PATH} shell wm density reset")
            InputPrompt("恢复完成,请按回车键继续/回到主页面").prompt()
            self.splash_screen()

    def splash_screen(self):
        os.system("cls")
        os.system("type firmware\\logo.txt | bin\\lolcat.exe")
        console.print("[bold red]小天才D3_Root工具箱 V1.0.0[/bold red]")
        console.print(
            f"[bold green]⌈ {self.hitokoto_data['hitokoto']}⌋ -- {self.hitokoto_data['from_who']}[/bold green]",
            justify="right",
        )
        with console.status("[green]正在等待您的设备连接......[/green]"):
            os.system(f"{ADB_PATH} wait-for-device")
        get_list = ListPrompt(
            "请选择您想要进行的操作:",
            choices=[
                Choice("一键Root"),
                Choice("安装应用"),
                Choice("刷入儿童微信License"),
                Choice("修复运行环境"),
                Choice("修改开机第一屏"),
                Choice("备份还原基带"),
                Choice("ADB命令行"),
                Choice("修改DPI"),
                Choice("退出"),
            ],
        ).prompt()
        if get_list.name == "一键Root":
            self.root()
        elif get_list.name == "安装应用":
            self.installapps()
        elif get_list.name == "刷入儿童微信License":
            self.flash_license()
        elif get_list.name == "修复运行环境":
            self.fix_env()
        elif get_list.name == "修改开机第一屏":
            self.change_boot_logo()
        elif get_list.name == "备份还原基带":
            self.backup_restore_modem()
        elif get_list.name == "ADB命令行":
            os.system(f"cmd /k cd /d {os.getcwd()}\\bin")
            self.splash_screen()
        elif get_list.name == "修改DPI":
            self.change_dpi()
        elif get_list.name == "退出":
            sys.exit()

    def run(self):
        try:
            self.splash_screen()
        except CancelledError:
            console.print("[bold green]退出程序[/bold green]")
        except KeyboardInterrupt:
            console.print("[bold green]退出程序[/bold green]")
