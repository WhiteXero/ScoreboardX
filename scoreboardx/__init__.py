import json
import os
import random
import time

from mcdreforged.api.all import *

xboard_version = '1.0.0'
xboard_help = [
    '§f§l======= §eScoreboardX §b{} §f======='.format(xboard_version),
    '§d§l[指令]',
    '!!xboard rotate §e§l<布尔值>§r§b: 启用或禁用计分板轮换显示功能',
    '!!xboard rotate config §e§l<选项> <选项值>§r§b: 设置计分板轮换显示方式',
    '!!xboard rotate list §e§l<操作> <计分项>§r§b: 设置计分板轮换的计分项',
    '!!xboard rotate apply§r§b: 执行所有更改',
    '§d§l[参数]',
    '§e§l<布尔值>§r§b: 一个布尔值，可使用 §fTrue / False.',
    '§e§l<选项> <选项值>§r§b: 用于轮换显示的设置项：',
    '   time <int>: 轮换间隔时间',
    '   sequence <sequentially | randomly>: 轮换顺序',
    '   position <below_name | sidebar | sidebar.team.color | list>: 轮换位置',
    '§e§l<操作>§r§b: 用于调整参与轮换的计分项：',
    '   show: 显示已配置的计分项列表',
    '   add: 增加计分项',
    '   remove: 移除计分项',
    '§e§l<计分项>§r§b: 在§u/scoreboard§w中创建的计分项.'
]
config_items = ['time', 'sequence', 'position', 'enable']
xboard_list = []
xboard_config = {}
team_color = ["black", "dark_blue", "dark_green", "dark_aqua", "dark_red", "dark_purple", "gold", "gray", "dark_gray",
              "blue", "green", "aqua", "red", "light_purple", "yellow", "white"]
terminate = False


# noinspection PyUnusedLocal
def on_load(server, params):
    server.logger.info('正在注册指令')
    server.register_help_message('!!xboard', 'ScoreboardX 使用帮助')
    global xboard_list, xboard_config
    server.logger.info('正在恢复文件配置')
    try:
        with open(os.path.join(server.get_data_folder(), 'xboard_config.json'), 'r', encoding='UTF-8') as conf:
            xboard_config = json.load(conf)
            conf.close()
        for i in config_items:
            server.logger.info('检查配置项 {} => {}'.format(i, xboard_config[i]))
    except FileNotFoundError:
        server.logger.warning('无法找到配置文件。这可能是由于您第一次运行此插件。')
        xboard_config = {
            "time": 1.0,
            "sequence": "sequentially",
            "position": "sidebar",
            "enable": False
        }
    except KeyError:
        server.logger.warning(
            '恢复配置文件时出错。这可能是由于您更新了插件，而配置文件与当前版本不匹配。已为您恢复为默认配置。')
        xboard_config = {
            "time": 1.0,
            "sequence": "sequentially",
            "position": "sidebar",
            "enable": False
        }
    server.logger.info('正在加载计分项')
    try:
        with open(os.path.join(server.get_data_folder(), 'xboard_list.txt'), 'r', encoding='UTF-8') as f:
            xboard_list = f.readlines()
            f.close()
            for i in range(0, len(xboard_list)):
                xboard_list[i] = xboard_list[i].rstrip('\n')
    except FileNotFoundError:
        server.logger.warning('计分项保存内容已失效。这可能是由于您第一次运行此插件。')
        xboard_list = []


def on_server_startup(server):
    server.logger.info('ScoreboardX运行中。')
    server.logger.warning('由于重复轮换会导致OP聊天栏大量刷屏，强烈建议您在 server.properties 中禁用 broadcast-console-to-ops 与 '
                          'broadcast-rcon-to-ops 选项。')
    # noinspection PyUnresolvedReferences
    x_run()


def x_run():
    server = ServerInterface.get_instance()
    if xboard_config['enable'] and xboard_list != []:
        if xboard_config['sequence'] == 'sequentially':
            i = 0
            while i <= len(xboard_list) and terminate is False:
                time.sleep(xboard_config['time'])
                # noinspection PyArgumentList
                server.execute(
                    'scoreboard objectives setdisplay {} {}'.format(xboard_config['position'], xboard_list[i]))
                i += 1
                if i == len(xboard_list):
                    i = 0
        elif xboard_config['sequence'] == 'randomly':
            while terminate is False:
                time.sleep(xboard_config['time'])
                # noinspection PyArgumentList
                server.execute(
                    'scoreboard objectives setdisplay {} {}'.format(xboard_config['position'],
                                                                    xboard_list[random.randint(0, len(list))]))


def on_unload(server):
    global xboard_list, xboard_config
    server.logger.info('正在保存文件配置')
    with open(os.path.join(server.get_data_folder(), 'xboard_config.json'), 'w', encoding='UTF-8') as conf:
        json.dump(xboard_config, conf)
        conf.close()
    with open(os.path.join(server.get_data_folder(), 'xboard_list.txt'), 'w', encoding='UTF-8') as f:
        for i in xboard_list:
            f.write(i + '\n')
        f.close()


def on_info(server, info):
    if info.is_user:
        if info.content == '!!xboard':
            if info.is_user and server.get_permission_level(info) < 2:
                x_reply(server, info, '§c您的权限不足。')
            else:
                for x_help in xboard_help:
                    server.reply(info, x_help)
                if server.is_rcon_running():
                    x_reply(server, info, '§aRCON已连接。')
                else:
                    x_reply(server, info, '§cRCON未连接。')
        elif info.content[:8] == '!!xboard' and info.content != '!!xboard':
            interpreter(server, info)


def x_reply(server, info, message):
    server.reply(info, '§l§d[ScoreboardX] §r§w{}'.format(message))


def interpreter(server, info):
    command = info.content.split()
    match command[1]:
        case 'rotate':
            rotate_interpreter(server, info)
        case _:
            x_reply(server, info, '§c无法解析命令。')


def rotate_interpreter(server, info):
    global xboard_list, xboard_config, terminate
    command = info.content.split()
    match command[2]:
        case 'True':
            xboard_config['enable'] = True
            x_reply(server, info, '计分板轮换设置为 §e启用 。')
        case 'False':
            xboard_config['enable'] = False
            x_reply(server, info, '计分板轮换设置为 §e禁用 。')
        case 'apply':
            if terminate is False:
                x_reply(server, info, '§a所有更改已执行。当前进程已终止，再次执行Apply操作运行进程。')
                terminate = True
            else:
                terminate = False
                x_run()
        case 'config':
            match command[3]:
                case 'time':
                    try:
                        timer = float(command[4])
                        xboard_config['time'] = timer
                        x_reply(server, info, '修改 §e计分板轮换间隔 §f为 §e{}s。'.format(timer))
                    except TypeError:
                        x_reply(server, info, '§c输入的值类型错误。')
                    except IndexError:
                        x_reply(server, info, '§c无法解析命令。')
                case 'position':
                    match command[4]:
                        case 'list':
                            xboard_config['position'] = 'list'
                            x_reply(server, info, '修改 §e计分板轮换位置 §f为 §e玩家Tab列表。')
                        case 'below_name':
                            xboard_config['position'] = 'below_name'
                            x_reply(server, info, '修改 §e计分板轮换位置 §f为 §e玩家名称下方。')
                        case 'sidebar':
                            xboard_config['position'] = 'sidebar'
                            x_reply(server, info, '修改 §e计分板轮换位置 §f为 §e全局侧边栏')
                        case _:
                            if command[4][13:] in team_color:
                                xboard_config['position'] = command[4]
                                x_reply(server, info,
                                        '修改 §e计分板轮换位置 §f为 §e队伍{}侧边栏'.format(command[4][13:]))
                            else:
                                x_reply(server, info, '§c无法解析命令。')
                case 'sequence':
                    try:
                        if command[4] == 'sequentially':
                            xboard_config['sequence'] = 'sequentially'
                            x_reply(server, info, '修改 §e计分板轮换顺序 §f为 §e顺序。')
                        elif command[4] == 'randomly':
                            xboard_config['sequence'] = 'randomly'
                            x_reply(server, info, '修改 §e计分板轮换顺序 §f为 §e乱序。')
                        else:
                            x_reply(server, info, '§c输入的值不存在。')
                    except IndexError:
                        x_reply(server, info, '§c无法解析命令。')
                case _:
                    x_reply(server, info, '§c无法解析命令。')
        case 'list':
            match command[3]:
                case 'show':
                    x_reply(server, info, '§e已加入到轮换列表的计分项：')
                    x_reply(server, info, str(xboard_list))
                case 'add':
                    try:
                        if object_check(server, 'in-game', command[4], info):
                            xboard_list.append(command[4])
                            x_reply(server, info, '添加了计分项 §e{} 。'.format(command[4]))
                        else:
                            x_reply(server, info, '计分项 §e{} §c不存在。'.format(command[4]))
                    except IndexError:
                        x_reply(server, info, '§c无法解析命令。')
                case 'remove':
                    try:
                        if object_check(server, 'inlist', command[4], info):
                            xboard_list.remove(command[4])
                            x_reply(server, info, '移除了计分项 §e{} 。'.format(command[4]))
                        else:
                            x_reply(server, info, '计分项 §e{} §c不存在。'.format(command[4]))
                    except IndexError:
                        x_reply(server, info, '§c无法解析命令。')
                case _:
                    x_reply(server, info, '§c无法解析命令。')
        case _:
            x_reply(server, info, '§c无法解析命令。')


def object_check(server, check_type, scoreboard_object, info):
    match check_type:
        case 'in-game':
            if server.is_rcon_running():
                # noinspection PyArgumentList
                scoreboard_list = server.rcon_query('scoreboard objectives add {} dummy 1'.format(scoreboard_object))
            else:
                x_reply(server, info,
                        '§c§l警告：§r§c由于服务器未启用RCON，游戏内计分项检查已被禁用。\n§r§b要开启RCON，请参阅：https://docs.mcdreforged.com/zh-cn'
                        '/latest/configuration.html#rcon')
                return True
            if scoreboard_list == 'An objective already exists by that name':
                return True
            else:
                server.execute('scoreboard objectives remove {}'.format(scoreboard_object))
                return False
        case 'inlist':
            if scoreboard_object in xboard_list:
                return True
    return False
