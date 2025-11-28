"""
帖子数据模型

使用Pydantic v2进行数据验证和序列化（底层使用Rust的pydantic-core）
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict


class PostMetadata(BaseModel):
    """帖子元数据"""
    view_count: int = Field(default=0, ge=0, description="浏览次数")
    follow_count: int = Field(default=0, ge=0, description="关注人数")
    upvote_count: int = Field(default=0, ge=0, description="点赞数")
    comment_count: int = Field(default=0, ge=0, description="评论/回答数量")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "view_count": 12500,
                "follow_count": 320,
                "upvote_count": 1580,
                "comment_count": 156
            }
        }
    )


class Post(BaseModel):
    """
    帖子/问题/文章数据模型

    适用于知乎问题、知乎文章、V2EX帖子等
    """
    # 基本信息
    platform: str = Field(..., description="平台名称（zhihu/v2ex/etc）")
    post_type: str = Field(..., description="帖子类型（question/article/topic）")
    url: str = Field(..., description="帖子URL")

    # 内容信息
    title: str = Field(..., min_length=1, description="标题")
    content: Optional[str] = Field(default=None, description="正文内容")

    # 作者信息
    author: Optional[str] = Field(default=None, description="作者用户名")
    author_url: Optional[str] = Field(default=None, description="作者主页URL")

    # 时间信息
    created_at: Optional[datetime] = Field(default=None, description="发布时间")
    scraped_at: datetime = Field(default_factory=datetime.now, description="采集时间")

    # 元数据
    metadata: PostMetadata = Field(default_factory=PostMetadata, description="帖子元数据")

    # 评论/回答数据
    comments: List['Comment'] = Field(default_factory=list, description="评论列表")

    # 相关性标记（人工确认）
    is_relevant: Optional[bool] = Field(default=None, description="是否与主题相关（人工标注）")
    relevance_note: Optional[str] = Field(default=None, description="相关性说明")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "platform": "zhihu",
                "post_type": "question",
                "url": "https://www.zhihu.com/question/123456",
                "title": "ChatGPT会让程序员失业吗？",
                "content": "最近ChatGPT很火...",
                "author": "张三",
                "created_at": "2023-02-15T10:30:00",
                "metadata": {
                    "view_count": 12500,
                    "comment_count": 156
                },
                "is_relevant": True,
                "relevance_note": "讨论AI对程序员岗位影响"
            }
        }
    )

    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """验证平台名称"""
        allowed = ['zhihu', 'v2ex', 'xiaohongshu', 'bilibili']
        if v.lower() not in allowed:
            raise ValueError(f"不支持的平台: {v}，允许的平台: {allowed}")
        return v.lower()

    @field_validator('post_type')
    @classmethod
    def validate_post_type(cls, v: str) -> str:
        """验证帖子类型"""
        allowed = ['question', 'article', 'topic', 'video']
        if v.lower() not in allowed:
            raise ValueError(f"不支持的帖子类型: {v}，允许的类型: {allowed}")
        return v.lower()

    def get_comment_count(self) -> int:
        """获取评论数量"""
        return len(self.comments)

    def update_metadata(self) -> None:
        """更新元数据中的评论计数"""
        self.metadata.comment_count = self.get_comment_count()

    def is_valid_for_analysis(self, min_comments: int = 100) -> bool:
        """
        检查是否适合用于分析

        Args:
            min_comments: 最少评论数要求

        Returns:
            是否符合要求
        """
        return (
            self.get_comment_count() >= min_comments and
            self.is_relevant is not False  # None或True都可以
        )


# 导入Comment以支持前向引用
from .comment import Comment

# 更新前向引用
Post.model_rebuild()
