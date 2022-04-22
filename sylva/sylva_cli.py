import json
import os
import re
from typing import Iterable

from rich.console import Console
from rich.theme import Theme

from ._log import log
from .sylva import Sylva
from .sylva_render import SylvaRender
from ._exception import UnknownCommand, UnexpectedCode

__all__ = ["SylvaCLI"]

console = Console(theme=Theme.read("theme.ini"))


class SylvaCLI:
    Debug = False

    def __init__(self) -> None:
        self.sylva = Sylva()
        config = dict()
        if os.path.exists("config.json"):
            with open("config.json") as f:
                config.update(json.load(f))
        if "token" in config:
            self.sylva.setToken(config["token"])
        else:
            config.update({"token": self.login()})
            with open("config.json", "wt") as f:
                json.dump(config, f)
        log.info("登录成功")

    def filter(self, what: Iterable, attr: str, only: str | Iterable[str]) -> Iterable:
        """过滤器

        Args:
            what (Iterable): 需要过滤的对象
            attr (str): 过滤的属性
            only (str | Iterable[str]): 在 `only` 中可不被过滤

        Returns:
            Iterable: _description_
        """
        if isinstance(only, str):
            only = {only}
        elif isinstance(only, Iterable):
            only = set(only)
        return filter(lambda i: i[attr] in only, what)

    def login(self) -> str:
        """登录

        Args:
            phone (str): 手机号

        Returns:
            str: token
        """
        phone = input("请输入手机号: ")
        senCode = self.sylva.sendCode(phone)
        log.info("验证码发送成功")
        validCode = input("请输入验证码: ")
        register = self.sylva.register(phone, validCode)
        token = register.json()["token"]
        return self.sylva.setToken(token)

    def createHole(self, content, **kwargs) -> None:
        """发布树洞（交互）

        Args:
            content (_type_): 内容

        Raises:
            UnexpectedCode: 异常
        """
        resp = self.sylva.createHole(content, **kwargs)
        if resp.status_code not in {200, 204}:
            raise UnexpectedCode(resp.json())

    def createHoleReply(self, pid: str, content: str, cid=None, **kwargs):
        """回复树洞（交互）

        Args:
            pid (str): 树洞 ID
            content (str): 内容
            cid (_type_, optional): 引用 ID

        Raises:
            UnexpectedCode: 异常
        """
        resp = self.sylva.createHoleReply(pid, content, cid)
        if resp.status_code not in {200, 204}:
            raise UnexpectedCode(resp.json())
        self.getHole(pid, **kwargs)

    def followHole(self, pid: str) -> None:
        """收藏树洞（交互）

        Args:
            pid (str): 树洞 ID
        """
        self.sylva.followHole(pid)

    def getHole(
        self,
        pid: str,
        onlyWho: str | Iterable[str] = None,
        onlyWhich: str | Iterable[str] = None,
        **kwargs,
    ) -> None:
        """获取树洞（交互）

        Args:
            pid (str): 树洞 ID
            onlyWho (str | Iterable[str], optional): 只看 `onlyWho`
            onlyWhich (str | Iterable[str], optional): 只看 `onlyWhich` 高校

        Raises:
            UnexpectedCode: 异常
        """
        render = SylvaRender.createContentTable()
        got = self.sylva.getHole(pid, **kwargs).json()
        if "code" in got:
            raise UnexpectedCode(got)
        render.addHole(got)
        if got["replies"]:
            replies = got["replies"]
            cites = {i["cid"]: i for i in replies}
            if onlyWho is not None:
                replies = self.filter(replies, "name", onlyWho)
            if onlyWhich is not None:
                replies = self.filter(replies, "school_name", onlyWhich)
            for i in replies:
                render.addHoleReply(i, cites)
        console.print(render)

    def getHoles(
        self, perPage: int = 20, onlyWhich: str | Iterable[str] = None, **kwargs
    ) -> None:
        """获取树洞列表（交互）

        Args:
            perPage (int, optional): 数量. Defaults to 20
            onlyWhich (str | Iterable[str], optional): 仅看 `onlyWhich` 高校

        Raises:
            UnexpectedCode: 异常
        """
        render = SylvaRender.createContentTable()
        got = self.sylva.getHoles(perPage=perPage, **kwargs).json()
        if "code" in got:
            raise UnexpectedCode(got)
        # 由于旧帖没有 school_name, 请不要在旧帖中使用这个方法
        if onlyWhich is not None:
            got = self.filter(got, "school_name", onlyWhich)
        for i in got:
            render.addHole(i)
        console.print(render)

    def unfollowHole(self, pid: str) -> None:
        """取消收藏树洞（交互）

        Args:
            pid (str): 树洞 ID
        """
        self.sylva.followHole(pid)

    def sendVote(self, pid: str, option: str):
        """投票（交互）

        Args:
            pid (str): 树洞 ID
            option (str): 选项

        Raises:
            UnexpectedCode: 异常
        """
        got = self.sylva.sendVote(pid, option).json()
        if "code" in got:
            raise UnexpectedCode(got)
        console.print(SylvaRender.createVoteTable(got))

    def getDevices(self) -> None:
        """获取设备列表（交互）

        Raises:
            UnexpectedCode: 异常
        """
        got = self.sylva.getDevices().json()
        if "code" in got:
            raise UnexpectedCode(got)
        console.print(SylvaRender.createDevicesTable(got))

    def kickDevice(self, uuid: str) -> None:
        """踢出设备（交互）

        Args:
            uuid (str): 设备 UUID
        """
        self.sylva.kickDevice(uuid)

    def downloadHoleImage(self, pid: str) -> None:
        """下载树洞图片（交互）

        Args:
            pid (str): 树洞 ID
        """
        got = self.sylva.getHole(pid).json()
        if "image" in got:
            self.sylva.downloadImage(got["image"]["src"], f"images/{got['pid']}")
            if got["replies"]:
                for i in got["replies"]:
                    if "image" in i:
                        self.sylva.downloadImage(i["image"]["src"], f"images/{pid}")
        else:
            raise Exception(got)

    def match(self, command: str) -> None:
        """交互选项

        Args:
            command (str): 参数

        Raises:
            UnknownCommand: 未知命令
        """
        # content 包含空格时需在两侧加引号
        command = re.findall(r"(['\"](.+)['\"])|([^ ]+)", command)
        command = list(i[1] if i[1] != "" else i[2] for i in command)
        match (command):
            # 发布树洞
            case ["c" | "create", content, *args]:
                kwargs = {args[i]: args[i + 1] for i in range(0, len(args), 2)}
                self.createHole(content, **kwargs)
            # 回复树洞
            case ["r" | "reply", pid, cid, content, *args]:
                kwargs = {args[i]: args[i + 1] for i in range(0, len(args), 2)}
                self.createHoleReply(pid, content, cid, **kwargs)
            # 回复树洞
            case ["r" | "reply", pid, content]:
                self.createHoleReply(pid, content)
            # 收藏树洞
            case ["f" | "follow", pid]:
                self.followHole(pid)
            # 获取树洞
            case ["h" | "hole", pid, *args]:
                kwargs = {args[i]: args[i + 1] for i in range(0, len(args), 2)}
                self.getHole(pid, **kwargs)
            # 获取树洞列表
            case ["l" | "list", perPage]:
                self.getHoles(perPage)
            # 获取树洞列表
            case ["l" | "list", *args]:
                kwargs = {args[i]: args[i + 1] for i in range(0, len(args), 2)}
                self.getHoles(**kwargs)
            # 取消收藏树洞
            case ["uf" | "unfollow", pid]:
                self.unfollowHole(pid)
            # 投票
            case ["v" | "vote", pid, option]:
                self.sendVote(pid, option)
            # 获取设备
            case ["d" | "devices"]:
                self.getDevices()
            # 踢出设备
            case ["kd" | "kick", uuid]:
                self.kickDevice(uuid)
            # 下载图片
            case ["i" | "image", pid]:
                self.downloadHoleImage(pid)
            # 调试模式
            case ["debug"]:
                # client 方便调试
                client = self.sylva.client
                console.log(
                    "Entered debug mode, you can press ^C or ^Z to exit debug mode"
                )
                while True:
                    try:
                        console.print(eval(input(">>> ")))
                    # ^C
                    except KeyboardInterrupt:
                        console.print()
                        log.info("Exited debug mode")
                        break
                    # ^Z
                    except EOFError:
                        log.info("Exited debug mode")
                        break
                    except SyntaxError as e:
                        log.error(e)
                        continue
            case []:
                return
            case _:
                raise UnknownCommand(f"未知命令：{command}")

    def main(self):
        """主循环

        Raises:
            e: 调试时抛出异常
        """
        while True:
            try:
                command = input("> ")
                self.match(command)
            # ^C
            except KeyboardInterrupt:
                break
            # ^Z
            except EOFError:
                break
            except Exception as e:
                if SylvaCLI.Debug:
                    log.exception(e)
                else:
                    log.error(e)
