import maya
from rich import box
from rich.table import Table

__all__ = ["SylvaRender"]


class SylvaRender:
    Style = {"show_header": False, "expand": True, "show_edge": False}

    def __init__(self):
        self.table = None

    @classmethod
    def createContentTable(cls) -> "SylvaRender":
        """创建内容表

        Returns:
            SylvaRender: 表
        """
        render = SylvaRender()
        render.table = Table(
            box=box.HORIZONTALS, show_header=False, show_lines=True, expand=True
        )
        # 请不要使用垂直居中！！！否则可能出现空行！！！丑陋的空行！！！
        render.table.add_column(ratio=20)
        render.table.add_column(ratio=80)
        return render

    @classmethod
    def createVoteTable(cls, vote: dict) -> "SylvaRender":
        """创建投票表

        Args:
            vote (dict): 投票

        Returns:
            SylvaRender: 表
        """
        render = SylvaRender()
        render.table = Table(box=box.MINIMAL, **SylvaRender.Style)

        for _ in vote["options"]:
            render.table.add_column(justify="center")

        if "voted" in vote:
            voted = vote["voted"]
            index = vote["options"].index(voted)
            vote["options"][index] = f"[voted]{vote['options'][index]}[/]"

        options = list(str(i) for i in vote["options"])
        results = list(str(i) for i in vote["results"])
        render.table.add_row(*options)
        if results[0] != "-1":
            render.table.add_row(*results)

        return render

    @classmethod
    def createDevicesTable(cls, devices: dict) -> "SylvaRender":
        """创建设备表

        Args:
            devices (dict): 设备

        Returns:
            SylvaRender: 表
        """
        render = SylvaRender()
        render.table = Table(box=box.MINIMAL, expand=True)
        render.table.add_column("UUID", justify="center")
        render.table.add_column("Login Time", justify="center")
        render.table.add_column("Name", justify="center")

        for i in devices:
            render.table.add_row(
                i["uuid"],
                maya.when(str(i["login_time"]), timezone="Asia/Shanghai").slang_time(),
                i["name"],
            )

        return render

    def addHole(self, hole: dict) -> None:
        """向内容表中添加树洞

        Args:
            self.table (Table): 内容表
            hole (dict): 树洞
        """
        tag = f'{hole["tag"]}' if "tag" in hole else ""
        schoolName = f'{hole["school_name"]}' if "school_name" in hole else ""

        createdAt = maya.when(
            str(hole["created_at"]), timezone="Asia/Shanghai"
        ).slang_time()

        hasImage = "[image]i[/]" if "image" in hole else ""
        hasVote = "[vote]v[/]" if "vote" in hole else ""
        followed = "followed" if hole["followed"] else "default"
        followersCount = f"[star]*[/] {hole['followers_count']}"
        repliesCount = f"[reply]>[/] {hole['replies_count']}"

        left = Table(box=None, **SylvaRender.Style)
        left.add_column(justify="right")
        left.add_row(f"[tag]{tag}[/][schoolName]{schoolName}[/]")
        left.add_row(f"{hasImage}{hasVote} [{followed}]{hole['pid']}[/]")
        left.add_row(f"{followersCount} | {repliesCount}")
        left.add_row(f"{createdAt}")

        right = Table(box=None, **SylvaRender.Style)
        right.add_column(overflow="fold")
        right.add_row(hole["content"])
        if "vote" in hole:
            right.add_row()
            right.add_row(self.createVoteTable(hole["vote"]))
        self.table.add_row(left, right)

    def addHoleReply(self, reply: dict, cites: dict) -> None:
        """向内容表中添加回复

        Args:
            self.table (Table): 内容表
            reply (dict): 单个回复
            cites (dict): 用于生成引用的所有回复
        """
        tag = f'{reply["tag"]}' if "tag" in reply else ""
        schoolName = f'{reply["school_name"]}' if "school_name" in reply else ""

        createdAt = maya.when(
            str(reply["created_at"]), timezone="Asia/Shanghai"
        ).slang_time()

        hasImage = "[image]i[/]" if "image" in reply else ""

        left = Table(box=None, **SylvaRender.Style)
        left.add_column(justify="right")
        left.add_row(f"[tag]{tag}[/][schoolName]{schoolName}[/]")
        left.add_row(
            f'{hasImage} [name]{reply["name"]}[/][at]@[/][cid]{reply["cid"]}[/]'
        )
        left.add_row(f"{createdAt}")

        right = Table(box=None, **SylvaRender.Style)
        right.add_column(overflow="fold")
        if "reply_cid" in reply:
            cite = cites[reply["reply_cid"]]
            right.add_row(f"[reply]>[/] [name]{cite['name']}[/]: {cite['content']}")
            right.add_row()
        right.add_row(reply["content"])
        self.table.add_row(left, right)

    # See https://rich.readthedocs.io/en/stable/protocol.html#console-customization
    def __rich__(self):
        return self.table
