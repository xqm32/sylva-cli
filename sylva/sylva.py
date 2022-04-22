import os
from typing import Literal

import httpx

from ._log import log
from ._login import loginRequired, willLogin

__all__ = ["Sylva"]


class Sylva:
    APIRoot = "https://api.treehollow.net/v5"
    IMGRoot = "https://img.treehollow.net"
    Global = "00000001-0001-0001-0001-000000000001"
    School = "00000000-0000-0000-0000-000000000001"

    def __init__(self) -> None:
        self.client = httpx.Client(proxies={"all://": None})
        self.client.headers.update({"modelname": "Sylva CLI"})
        self.logged = set()

    @willLogin("Sylva")
    def setToken(self, token: str) -> str:
        """使用 token 登录

        Args:
            token (str): token

        Returns:
            str: token
        """
        self.client.headers.update({"token": token})
        return token

    def sendCode(self, phone: str) -> httpx.Response:
        """发送验证码

        Args:
            phone (str): 手机号

        Returns:
            httpx.Response: 响应
        """
        payload = {"method": "phone", "username": phone}
        sendCode = self.client.post(f"{Sylva.APIRoot}/auth/sendcode", json=payload)
        return sendCode

    def register(self, phone: str, validCode: str) -> httpx.Response:
        """注册/登录

        Args:
            phone (str): 手机号
            validCode (str): 验证码

        Returns:
            httpx.Response: 响应
        """
        payload = {"method": "phone", "username": phone, "valid_code": validCode}
        register = self.client.post(f"{Sylva.APIRoot}/auth/register", json=payload)
        return register

    @loginRequired("Sylva")
    def createHole(
        self, content: str, hid: str = Global, tag: str = ""
    ) -> httpx.Response:
        """发布树洞

        Args:
            content (str): 内容
            hid (str, optional): hid
            tag (str, optional): 标签

        Returns:
            httpx.Response: 响应
        """
        payload = {"content": content, "hid": hid, "tag": tag}
        holes = self.client.post(f"{Sylva.APIRoot}/holes", json=payload)
        return holes

    @loginRequired("Sylva")
    def createHoleReply(
        self, pid: str, content: str, replyCid: str = None
    ) -> httpx.Response:
        """回复树洞

        Args:
            pid (str): 树洞 ID
            content (str): 内容
            replyCid (str, optional): 引用 ID, `None` 表示不引用

        Returns:
            httpx.Response: 响应
        """
        payload = {"pid": pid, "content": content}
        if replyCid is not None:
            payload.update({"reply_cid": replyCid})
        replies = self.client.post(f"{Sylva.APIRoot}/holes/replies", json=payload)
        return replies

    @loginRequired("Sylva")
    def createHoleVote(self):
        pass

    @loginRequired("Sylva")
    def followHole(self, pid: str) -> httpx.Response:
        """收藏树洞

        Args:
            pid (str): 树洞 ID

        Returns:
            httpx.Response: 响应
        """
        payload = {"pid": pid}
        follow = self.client.put(f"{Sylva.APIRoot}/holes/follow", params=payload)
        return follow

    @loginRequired("Sylva")
    def getHole(self, pid: str) -> httpx.Response:
        """获取树洞

        Args:
            pid (str): 树洞 ID

        Returns:
            httpx.Response: 响应
        """
        payload = {"pid": pid}
        detail = self.client.get(f"{Sylva.APIRoot}/holes/detail", params=payload)
        return detail

    @loginRequired("Sylva")
    def getHoles(
        self,
        type: Literal["timeline", "trending", "replied", "following"] = "timeline",
        perPage: int = 20,
        after: str = None,
        search: str = None,
        hid: str = Global,
    ) -> httpx.Response:
        """获取树洞列表

        Args:
            type (Literal[timeline, trending, replied, following], optional):
                `timeline` 为时间线, `trending` 为热度, `replied` 为回复, `following` 为关注
            perPage (int, optional): 数量
            after (str, optional): 从 `after` 开始获取, None 为从时间线获取
            search (str, optional): 搜索关键字
            hid (str, optional): hid

        Returns:
            httpx.Response: 响应
        """
        payload = {
            "type": type,
            "per_page": perPage,
            "after": after,
            "search": search,
            "hid": hid,
        }
        holes = self.client.get(f"{Sylva.APIRoot}/holes", params=payload)
        return holes

    @loginRequired("Sylva")
    def reportHole(self, pid: str, reason: str) -> httpx.Response:
        """举报树洞

        Args:
            pid (str): 树洞 ID
            reason (str): 原因

        Returns:
            httpx.Response: 响应
        """
        payload = {"pid": pid, "reason": reason, "action": "report"}
        reports = self.client.post(f"{Sylva.APIRoot}/holes/reports", json=payload)
        return reports

    @loginRequired("Sylva")
    def unfollowHole(self, pid: str) -> httpx.Response:
        """取消收藏树洞

        Args:
            pid (str): 树洞 ID

        Returns:
            httpx.Response: 响应
        """
        payload = {"pid": pid}
        follow = self.client.delete(f"{Sylva.APIRoot}/holes/follow", params=payload)
        return follow

    @loginRequired("Sylva")
    def getHollows(self) -> httpx.Response:
        """获取全国树洞

        Returns:
            httpx.Response: 响应
        """
        hollows = self.client.get(f"{Sylva.APIRoot}/hollows")
        return hollows

    @loginRequired("Sylva")
    def getNotifications(self) -> httpx.Response:
        """获取通知

        Returns:
            httpx.Response: 响应
        """
        notifications = self.client.get(f"{Sylva.APIRoot}/user/notifications")
        return notifications

    @loginRequired("Sylva")
    def getSystemMessages(self) -> httpx.Response:
        """获取系统通知

        Returns:
            httpx.Response: 响应
        """
        systemMessages = self.client.get(f"{Sylva.APIRoot}/user/system-messages")
        return systemMessages

    # 此 API 无效
    @loginRequired("Sylva")
    def getConfig(self) -> httpx.Response:
        """读取配置

        Returns:
            httpx.Response: 响应
        """
        config = self.client.get(f"{Sylva.APIRoot}/user/config")
        return config

    @loginRequired("Sylva")
    def getDevices(self) -> httpx.Response:
        """获取登陆设备

        Returns:
            httpx.Response: 响应
        """
        devices = self.client.get(f"{Sylva.APIRoot}/user/devices")
        return devices

    @loginRequired("Sylva")
    def kickDevice(self, uuid: str) -> httpx.Response:
        """踢出登录设备

        Args:
            uuid (str): 设备 UUID

        Returns:
            httpx.Response: 响应
        """
        payload = {"uuid": uuid}
        devices = self.client.delete(f"{Sylva.APIRoot}/user/devices", params=payload)
        return devices

    @loginRequired("Sylva")
    def logout(self, device=None) -> httpx.Response:
        """登出

        Returns:
            httpx.Response: _description_
        """
        payload = {"device": device}
        devices = self.client.delete(f"{Sylva.APIRoot}/user/devices", params=payload)
        return devices

    @loginRequired("Sylva")
    def readNotifications(self) -> httpx.Response:
        """已读通知

        Returns:
            httpx.Response: 响应
        """
        payload = {"type": "my"}
        read = self.client.post(
            f"{Sylva.APIRoot}/user/notifications/read", json=payload
        )
        return read

    @loginRequired("Sylva")
    def sendVote(self, pid: str, option: str) -> httpx.Response:
        """投票树洞

        Args:
            pid (str): 树洞 ID
            option (str): 选项

        Returns:
            httpx.Response: 响应
        """
        payload = {"pid": pid, "option": option}
        votes = self.client.post(f"{Sylva.APIRoot}/holes/votes", json=payload)
        return votes

    @loginRequired("Sylva")
    def downloadImage(self, src: str, path: str = "images") -> None:
        """下载图片

        Args:
            src (str): 链接
            path (str, optional): 保存路径
        """
        if not os.path.exists(path):
            os.makedirs(path)
        image = self.client.get(f"{Sylva.IMGRoot}/{src}")
        with open(f"{path}/{src.split('/')[-1]}", "wb") as f:
            f.write(image.content)
        log.info(f"图片已保存至 {path}/{src.split('/')[-1]}")
