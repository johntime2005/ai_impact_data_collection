/**
 * 知乎问题数据提取器 - 浏览器控制台脚本
 *
 * 使用方法：
 * 1. 在浏览器中打开知乎问题页面（如 https://www.zhihu.com/question/570403406）
 * 2. 按F12打开开发者工具，切换到Console标签
 * 3. 复制整个脚本内容，粘贴到控制台
 * 4. 按回车执行
 * 5. 脚本会自动提取数据并复制到剪贴板
 * 6. 粘贴给猫娘工程师即可！
 */

(function() {
    console.log('🔍 开始提取知乎问题数据...');

    try {
        // 提取问题信息
        const questionTitle = document.querySelector('h1.QuestionHeader-title')?.innerText ||
                            document.querySelector('.QuestionHeader-main .QuestionHeader-title')?.innerText ||
                            document.title.split(' - ')[0];

        const questionUrl = window.location.href.split('?')[0]; // 移除查询参数

        const questionId = questionUrl.match(/question\/(\d+)/)?.[1];

        // 提取回答数量
        const answerCountText = document.querySelector('.List-headerText')?.innerText ||
                               document.querySelector('.QuestionHeader-Comment')?.innerText ||
                               '0';
        const answerCount = parseInt(answerCountText.match(/\d+/)?.[0] || '0');

        // 提取前N个回答（最多20个）
        const answers = [];
        const answerElements = document.querySelectorAll('.List-item');

        let extractedCount = 0;
        for (let i = 0; i < Math.min(answerElements.length, 20); i++) {
            const elem = answerElements[i];

            // 提取作者信息
            const author = elem.querySelector('.AuthorInfo-name')?.innerText ||
                          elem.querySelector('.UserLink-link')?.innerText ||
                          '匿名用户';

            // 提取回答内容（截取前500字）
            const contentElem = elem.querySelector('.RichContent-inner');
            let content = '';
            if (contentElem) {
                content = contentElem.innerText
                    .replace(/\n+/g, ' ')  // 移除换行
                    .replace(/\s+/g, ' ')   // 合并空格
                    .trim()
                    .substring(0, 500);     // 截取前500字
            }

            // 提取点赞数
            const voteText = elem.querySelector('.VoteButton--up')?.innerText || '0';
            const voteCount = parseInt(voteText.replace(/[^\d]/g, '') || '0');

            if (content && content.length > 10) {  // 过滤掉太短的回答
                answers.push({
                    author: author,
                    content: content,
                    upvotes: voteCount,
                    created_at: new Date().toISOString()  // 知乎不容易提取时间，用当前时间
                });
                extractedCount++;
            }
        }

        // 构建结果
        const result = {
            platform: "zhihu",
            type: "question",
            url: questionUrl,
            question_id: questionId,
            scraped_at: new Date().toISOString(),
            title: questionTitle,
            answer_count: answerCount,
            answers: answers,
            is_relevant: true,
            relevance_note: "手动添加 - 需确认相关性"
        };

        // 转换为JSON字符串
        const jsonStr = JSON.stringify(result, null, 2);

        // 复制到剪贴板
        navigator.clipboard.writeText(jsonStr).then(() => {
            console.log('✅ 数据提取成功！');
            console.log(`📊 问题: ${questionTitle}`);
            console.log(`📝 提取了 ${extractedCount} 个回答`);
            console.log(`📋 数据已复制到剪贴板，请粘贴给猫娘工程师！`);
            console.log('\n预览数据：');
            console.log(result);
        }).catch(err => {
            console.error('❌ 复制失败，请手动复制下面的JSON数据：');
            console.log(jsonStr);
        });

    } catch (error) {
        console.error('❌ 提取失败:', error);
        console.log('请确保：');
        console.log('1. 你在知乎问题页面上');
        console.log('2. 页面已经完全加载');
        console.log('3. 浏览器支持剪贴板API');
    }
})();
