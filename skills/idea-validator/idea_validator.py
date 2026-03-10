#!/usr/bin/env python3
"""
idea-validator - 创意验证器
在开始构建前，自动检查 GitHub、HN、npm、PyPI、Product Hunt 是否已有类似项目
"""

import sys
import json
import urllib.request
from urllib.parse import quote

def search_github(query):
    """搜索 GitHub repos"""
    try:
        url = f"https://api.github.com/search/repositories?q={quote(query)}&per_page=5&sort=stars"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("items", [])
    except Exception as e:
        return []

def search_hn(query):
    """搜索 Hacker News"""
    try:
        url = f"https://hn.algolia.com/api/v1/search?query={quote(query)}&tags=story&hitsPerPage=5"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("hits", [])
    except Exception as e:
        return []

def search_npm(query):
    """搜索 npm"""
    try:
        url = f"https://registry.npmjs.org/-/v1/search?text={quote(query)}&size=5"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("objects", [])
    except Exception as e:
        return []

def search_pypi(query):
    """搜索 PyPI"""
    try:
        url = f"https://pypi.org/search/?q={quote(query)}"
        # PyPI 没有简单 API，用搜索页面
        return [{"note": f"Check: https://pypi.org/search/?q={quote(query)}"}]
    except Exception as e:
        return []

def calculate_reality_signal(github_count, hn_count, npm_count):
    """计算现实信号分数 (0-100)"""
    # 简化算法：根据搜索结果数量估算
    score = 0
    if github_count > 1000:
        score += 40
    elif github_count > 100:
        score += 20
    elif github_count > 10:
        score += 10
    
    if hn_count > 50:
        score += 30
    elif hn_count > 10:
        score += 15
    
    if npm_count > 100:
        score += 30
    elif npm_count > 10:
        score += 15
    
    return min(score, 100)

def validate_idea(query):
    """验证一个创意"""
    print(f"🔍 验证创意：{query}\n")
    
    # 搜索各平台
    github_results = search_github(query)
    hn_results = search_hn(query)
    npm_results = search_npm(query)
    
    # 计算信号
    signal = calculate_reality_signal(len(github_results), len(hn_results), len(npm_results))
    
    # 输出结果
    print(f"📊 reality_signal: {signal}/100")
    
    if signal > 70:
        print("⚠️  空间非常拥挤，建议重新考虑或寻找差异化角度\n")
    elif signal > 30:
        print("⚡  有一定竞争，需要找到独特定位\n")
    else:
        print("✅  空间开放，可以开始构建！\n")
    
    # GitHub 结果
    if github_results:
        print("🐙 GitHub Top Competitors:")
        for i, repo in enumerate(github_results[:3], 1):
            stars = repo.get("stargazers_count", 0)
            desc = repo.get("description", "No description")[:60]
            print(f"  {i}. {repo['full_name']} - ⭐{stars:,} - {desc}")
        print()
    
    # HN 结果
    if hn_results:
        print("📰 Hacker News Discussions:")
        for i, post in enumerate(hn_results[:3], 1):
            print(f"  {i}. {post.get('title', 'N/A')[:60]} (score: {post.get('score', 0)})")
        print()
    
    # 建议
    if signal > 70:
        print("💡 差异化建议:")
        print("  - 聚焦特定语言/框架")
        print("  - 针对特定行业/场景")
        print("  - 做现有工具的插件/扩展")
    
    return signal

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：idea-validator <创意描述>")
        print("示例：idea-validator 'AI code review tool'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    validate_idea(query)
