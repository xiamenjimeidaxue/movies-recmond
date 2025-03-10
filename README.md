# 电影推荐系统

## 项目简介
本项目实现了一个基于用户评分和协同过滤算法的电影推荐系统。系统能够根据用户的评分历史，为其提供个性化的电影推荐。

## 功能概述
- 用户注册与登录
- 浏览热门电影
- 个性化电影推荐
- 用户对电影进行评分

## 技术架构
- **后端**：Python + Flask + Spark MLlib
- **数据库**：MySQL
- **前端**：HTML/CSS/JavaScript
- **推荐算法**：基于 Spark MLlib 的 ALS 协同过滤算法

## 使用指南

### 用户使用手册

#### 注册与登录
1. 访问项目首页
2. 点击注册按钮，输入用户名和密码完成注册
3. 注册成功后，使用新账号登录系统

#### 浏览热门电影
登录后，系统首页会展示热门电影列表，点击电影海报可查看详情

#### 电影评分
1. 在首页点击“电影评分”按钮
2. 对展示的电影进行评分（0-5分）
3. 评分完成后，点击提交按钮

#### 查看推荐
1. 提交评分后，系统会更新个性化推荐列表
2. 在首页的“个性推荐”区域查看推荐的电影

## 开发者使用手册

### 环境准备

#### 克隆项目仓库
确保你的设备已安装Git，然后使用以下命令克隆项目仓库：
```bash
git clone https://github.com/your-repo-url/movies-recmond.git
```
#### 配置环境
详细参考文件夹word文档4.2内容
