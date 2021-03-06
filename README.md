# 论文学者数据信息爬取工具
（回顾整理贴）

## 使用技术：urllib、pymysql、Levenshtein编辑距离

## 各函数功能介绍
**addAlterData**: 脚本、用于合并两个数据库的信息

**checkKeys**: 检查爬虫爬取Scopus API 是否因为key不足而出现异常

**clawler_tools**: 从Scopus学术网利用API爬取论文信息，转换HTML为JSON，XML的工具

**databaseIO**: 封装mysql数据库连接与操作方法，包括计数，存储，查询

**mainTest**:主函数，入口函数，先利用标题从scopus填充文章信息，

**mutilThreadMain**: 多线程处理更新数据，线程池线程数由MainTread的run()决定，每个线程对论文与搜索列表的更新由SingleThread的run()决定

**scopusSearch**: 利用Scopus高级检索命令获取文章信息，把该信息存放到数据库待检索详细文章信息的列表中

**scopusSupplyData**: 不存在scopus 文章ID时，从Semantic库中检索对应文章，如果有标题完全匹配或者模糊匹配的文章对应，
                      在scopus中采用文章标题查找、作者查找的方式获取作者与机构信息，并调用addArticle，UpdateSQL更新到数据库中

**scopusTitleGetsid**: 利用标题在scopus库中查找对应论文ID（sid），并更新检索列表中sid与flag

**scopusWholeInfo**: 将Scopus中利用ID找到的文章对应的文章信息，作者列表，机构列表从HTML状态处理成存入数据库中的字典、列表

**searchBykeyword**: 利用部分已知信息定义Scopus高级检索语句，用于检索

**semanticGetTitle**: 利用标题信息，从semantic库中获取作者、关键词、引用、年份、出版机构等信息，用于scopusSupplyData

**Settings**: 一些基本配置，包括用户，密码，Scopus key等

**taskAssign**: 将某一领域（例如：人工智能领域）将文章按照年份、文章类型、机构所在国家，将文章划分出不同层次的任务。任务参考saveTask.txt文件

**taskIntegration**: 整合Scopus子命令处理任务，一组子命令的任务总数小于某个固定值，把这些子命令通过OR合并处理

**taskManage**: 对任务列表【任务数量，对应Scopus子命令】的数据库查询与存储

**saveTask.txt**: 存放的是scopus的高级检索方式划分的文章检索，【序号，文章数量，子命令】
