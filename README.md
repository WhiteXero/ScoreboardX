# ScoreboardX
让计分板再次伟大——
此插件为计分板增加了一些小小的功能。若遇到bug请提交issue，会尽快修复！

## Todo
1. [ ] 计分板显示改进
2. [ ] 不同计分板综合、联系
3. [ ] 轮换增强

## 用法
在命令栏输入 `!!xboard` 获取更多帮助。

## 注意事项
* 此插件需要启用`rcon`。您可以依照[MCDR官方文档](https://docs.mcdreforged.com/zh-cn/latest/configuration.html#rcon)与[此专栏](https://www.bilibili.com/read/cv21900416/)进行配置。
* 建议在`server.properties`中禁用`broadcast-console-to-ops`与`broadcast-rcon-to-ops`，避免OP聊天栏刷屏。
* 首次启动时，会自动创建默认配置，此时提示“无法找到配置文件”为正常现象。
* `randomly`模式依赖于Python`randint()`函数，可能会随机到重复项目，为正常现象。