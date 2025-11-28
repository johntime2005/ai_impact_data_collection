"""
评论/回答数据模型

使用Pydantic v2进行数据验证和序列化
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Comment(BaseModel):
    """
    评论/回答数据模型

    适用于知乎回答、V2EX回复等
    """
    # 基本信息
    content: str = Field(..., min_length=1, description="评论内容")
    author: str = Field(..., description="评论作者")

    # 可选信息
    author_url: Optional[str] = Field(default=None, description="作者主页URL")
    comment_url: Optional[str] = Field(default=None, description="评论URL")

    # 互动数据
    upvotes: int = Field(default=0, ge=0, description="点赞数")
    downvotes: int = Field(default=0, ge=0, description="踩/反对数")

    # 时间信息
    created_at: Optional[datetime] = Field(default=None, description="发布时间")
    created_at_text: Optional[str] = Field(default=None, description="发布时间文本（如'2小时前'）")

    # 元数据
    is_author_reply: bool = Field(default=False, description="是否为作者回复")
    reply_to: Optional[str] = Field(default=None, description="回复给谁")

    # 文本分析相关（后续填充）
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1, description="情感得分 [-1, 1]")
    contains_keywords: Optional[bool] = Field(default=None, description="是否包含关键词")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "我认为AI不会完全取代程序员，但会改变我们的工作方式...",
                "author": "李四",
                "upvotes": 235,
                "created_at": "2023-03-10T15:20:00",
                "is_author_reply": False
            }
        }
    )

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """验证评论内容"""
        # 去除首尾空白
        v = v.strip()
        if len(v) == 0:
            raise ValueError("评论内容不能为空")
        return v

    def get_net_votes(self) -> int:
        """获取净赞数（赞-踩）"""
        return self.upvotes - self.downvotes

    def is_high_quality(self, min_upvotes: int = 10, min_length: int = 50) -> bool:
        """
        判断是否为高质量评论

        Args:
            min_upvotes: 最少点赞数
            min_length: 最少字符数

        Returns:
            是否为高质量评论
        """
        return (
            self.upvotes >= min_upvotes and
            len(self.content) >= min_length and
            self.get_net_votes() > 0
        )

    def get_content_preview(self, max_length: int = 100) -> str:
        """
        获取评论内容预览

        Args:
            max_length: 最大长度

        Returns:
            预览文本
        """
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
