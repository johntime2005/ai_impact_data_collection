"""
Reddit数据采集脚本 - 使用Playwright浏览器自动化

通过已登录的浏览器会话采集Reddit帖子和评论
需要先在浏览器中登录Reddit

使用方法:
1. 确保已通过Playwright打开并登录Reddit
2. 运行此脚本采集数据
"""

import json
import time
from datetime import datetime
from pathlib import Path
from loguru import logger


# 目标帖子URL列表（评论数≥100的AI对程序员影响相关帖子）
TARGET_POSTS = [
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/1mk8zj6/the_fact_that_chatgpt_5_is_barely_an_improvement/",
        "title": "The fact that ChatGPT 5 is barely an improvement shows that AI won't replace software engineers.",
        "comments": 881
    },
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/1i0goqm/why_are_ai_companies_obsessed_with_replacing/",
        "title": "Why are AI companies obsessed with replacing software engineers?",
        "comments": 699
    },
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/1m5kqv2/softbank_1000_ai_agents_replace_1_job_one_billion/",
        "title": "Softbank: 1,000 AI agents replace 1 job. One billion AI agents are set to be deployed this year.",
        "comments": 478
    },
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/1mlp72s/do_you_feel_the_vibe_shift_introduced_by_gpt5/",
        "title": "Do you feel the vibe shift introduced by GPT-5?",
        "comments": 396
    },
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/1kqrell/bill_gates_says_ai_wont_replace_programmers/",
        "title": "Bill gates says AI won't replace programmers",
        "comments": 383
    },
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/1b8yqym/addressing_the_whole_ai_will_replace_us_concern/",
        "title": "Addressing the whole 'AI will replace us' concern",
        "comments": 369
    },
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/1eoyz5l/be_totally_honest_people_who_are_at_least_mid/",
        "title": "Be totally honest, people who are at least Mid level, do you guys use LLM e.g. chatGPT?",
        "comments": 333
    },
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/14kia3e/an_excerpt_from_my_companys_annual_visions_and/",
        "title": "An Excerpt from my Company's Annual Visions and Goals Meeting (regarding AI displacement)",
        "comments": 313
    },
    {
        "url": "https://www.reddit.com/r/cscareerquestions/comments/1c0uzql/regarding_the_flood_of_will_ai_replace_us/",
        "title": "Regarding the flood of 'Will AI replace us'.",
        "comments": 308
    },
]


# JavaScript代码：在Reddit帖子页面提取数据
EXTRACT_POST_JS = """
() => {
    const result = {
        platform: 'reddit',
        type: 'submission',
        url: window.location.href,
        subreddit: '',
        scraped_at: new Date().toISOString(),
        title: '',
        content: '',
        author: '',
        created_at: '',
        upvotes: 0,
        comment_count: 0,
        comments: [],
        is_relevant: true,
        relevance_note: 'Playwright浏览器采集 - AI对程序员影响相关讨论'
    };

    try {
        // 提取subreddit
        const subredditMatch = window.location.href.match(/\\/r\\/([^\\/]+)/);
        if (subredditMatch) {
            result.subreddit = subredditMatch[1];
        }

        // 提取标题
        const titleElem = document.querySelector('h1[id^="post-title"]') ||
                         document.querySelector('[data-testid="post-title"]') ||
                         document.querySelector('h1');
        if (titleElem) {
            result.title = titleElem.innerText.trim();
        }

        // 提取帖子内容
        const contentElem = document.querySelector('[data-testid="post-content"]') ||
                          document.querySelector('[slot="text-body"]') ||
                          document.querySelector('.RichTextJSON-root');
        if (contentElem) {
            result.content = contentElem.innerText.trim();
        }

        // 如果没有找到内容，尝试其他选择器
        if (!result.content) {
            const paragraphs = document.querySelectorAll('main p');
            if (paragraphs.length > 0) {
                result.content = Array.from(paragraphs)
                    .map(p => p.innerText.trim())
                    .filter(t => t.length > 20)
                    .join('\\n\\n');
            }
        }

        // 提取作者
        const authorLink = document.querySelector('a[href*="/user/"]');
        if (authorLink) {
            const authorMatch = authorLink.href.match(/\\/user\\/([^\\/]+)/);
            if (authorMatch) {
                result.author = authorMatch[1];
            }
        }

        // 提取时间
        const timeElem = document.querySelector('time');
        if (timeElem) {
            result.created_at = timeElem.getAttribute('datetime') || timeElem.innerText;
        }

        // 提取评论（顶级评论）
        const commentElements = document.querySelectorAll('[id^="comment-tree-content-anchor"]');
        let commentCount = 0;

        // 如果上面的选择器不工作，尝试其他方式
        if (commentElements.length === 0) {
            // 尝试获取所有评论容器
            const allComments = document.querySelectorAll('shreddit-comment');
            allComments.forEach((commentEl, index) => {
                if (commentCount >= 100) return;

                try {
                    const authorEl = commentEl.querySelector('a[href*="/user/"]');
                    const contentEl = commentEl.querySelector('[slot="comment"]') ||
                                     commentEl.querySelector('[id*="comment-content"]');
                    const voteEl = commentEl.querySelector('[score]') ||
                                  commentEl.querySelector('faceplate-number');

                    if (contentEl && contentEl.innerText.trim().length > 5) {
                        result.comments.push({
                            author: authorEl ? authorEl.innerText.replace('u/', '').trim() : '[deleted]',
                            content: contentEl.innerText.trim().substring(0, 1000),
                            upvotes: voteEl ? parseInt(voteEl.getAttribute('number') || voteEl.innerText.replace(/[^0-9-]/g, '') || '0') : 0,
                            created_at: new Date().toISOString()
                        });
                        commentCount++;
                    }
                } catch (e) {
                    console.error('Error extracting comment:', e);
                }
            });
        }

        result.comment_count = commentCount;

    } catch (error) {
        result.error = error.message;
    }

    return result;
}
"""


def save_posts(posts, output_file):
    """保存帖子数据到JSON文件"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    logger.info(f"💾 数据已保存到: {output_path}")
    logger.info(f"📊 共保存 {len(posts)} 个帖子")


def main():
    """主函数 - 显示采集说明"""
    logger.info("🚀 Reddit Playwright采集器")
    logger.info("")
    logger.info("使用方法:")
    logger.info("1. 通过Claude Code的Playwright工具打开并登录Reddit")
    logger.info("2. 导航到每个帖子页面")
    logger.info("3. 使用browser_evaluate执行EXTRACT_POST_JS提取数据")
    logger.info("4. 将提取的数据保存到JSON文件")
    logger.info("")
    logger.info(f"目标帖子数量: {len(TARGET_POSTS)}")
    logger.info("")
    logger.info("目标帖子列表:")
    for i, post in enumerate(TARGET_POSTS, 1):
        logger.info(f"  {i}. [{post['comments']}评论] {post['title'][:50]}...")


if __name__ == "__main__":
    main()
