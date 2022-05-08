from spider_func import getHTMLText
from threading import Thread
from re import sub as re_sub
from time import time
import os

line = '-' * 12


def novel_name(url):
    # 要收集信息：小说名，作者，简介，小说类型，状态，最后更新时间，*最后章节
    # 必要的，提供给程序的信息：小说名，最后章节
    html = getHTMLText(url)

    small_sub = lambda string, start, end: string.split(start)[-1].split(end)[0]

    head = small_sub(html, '<head>', '</head>')
    head = head.split('</title>')[-1]
    head = re_sub(' ', '', re_sub('"', '', re_sub('>', '', re_sub('<', '', head))))
    # 去掉：空格，<,>,双引号。主要是为了我方便

    head = re_sub('metaproperty=og:', '', head)

    name = small_sub(head, 'book_namecontent=', '/')
    author = small_sub(head, 'authorcontent=', '/')
    description = small_sub(head, 'descriptioncontent=', '/')
    category = small_sub(head, 'categorycontent=', '/')
    status = small_sub(head, 'statuscontent=', '/')
    update_time = small_sub(head, 'update_timecontent=', '/')
    latest_chapter = int(small_sub(head, 'latest_chapter_urlcontent=', '.html/').split('/')[-1])

    _name = name
    _latest_chapter = latest_chapter
    _book_info = '{0}\n\n{1}\t作者：{2}\n简介：{3}\n小说类型：{4}\n状态：{5}\n最后更新时间：{6}\n最后更新章节：{7}'.format(
        line, name, author, description, category, status, update_time, str(latest_chapter))

    return _name, _latest_chapter, _book_info


def fetch(url):
    html = getHTMLText(url)

    if '本章由于字数太少，暂不显示。如果你觉得本章比较重要，可以选择左下方报错章节，系统将在十秒内自动处理。' in html:
        return line + '\n\n' + '!!!本章字数过短，未被显示' + '\n\n'
    elif 'DogError!' == html:
        return line + '\n\n' + '请求错误!' + '\n\n'
    # 这是笔趣阁的问题，不是我的问题，有很多都会这么显示
    # 如果没有上述if语句，可能会导致找不到标题而报错
    # 这样的网址可参考：https://www.bige7.com/book/1638/57.html

    # 文章内容
    u1 = html.split('<div id="chaptercontent" class="Readarea ReadAjax_content">')[-1]
    u1 = u1.split('<p class="readinline">')[0]
    u1 = '\n'.join(u1.split('<br />'))
    u1 = ''.join(u1.split('\t'))
    u1 = '“'.join(u1.split('&ldquo;'))      # 左引号
    u1 = '”'.join(u1.split('&rdquo;'))      # 右引号
    u1 = '...'.join(u1.split('&hellip;'))   # 省略号

    # 文章标题
    u2 = html.split('<h1 class="wap_none">')[-1]
    u2 = u2.split('</h1>')[0]

    return line + '\n' * 2 + u2 + '\n' * 2 + u1


def range_download(start, end, _book_info=''):
    # 不填_book_info就是没有简介，用于更新模式
    threads_list = []
    task = list(range(start, end + 1))

    for i in task:  # 创建任务
        t = Thread(target=tn, args=(i,))
        threads_list.append(t)

    print('启动线程 |', end='')
    i = 0

    for s in threads_list:  # 启动任务
        s.start()
        # 进度条↓
        i += 1
        if i >= round(len(task) / 15):
            i = 0
            print('-', end='')

    i = 0
    print('|\n开始下载 |', end='')

    for s in threads_list:  # 等待任务结束
        s.join()
        # 进度条↓
        i += 1
        if i >= round(len(task) / 15):
            i = 0
            print('-', end='')

    print('|\n')

    text = _book_info + '\n\n'
    for num in task:
        text += text_dict[num]

    return text


def tn(chapter: int):
    chapter_url = _url + str(chapter) + '.html'
    text_dict.setdefault(chapter, fetch(chapter_url))


def save(root, text, title, mode='w'):
    if not os.path.exists(root):
        os.makedirs(root)
    with open(os.path.join(root, title + '.txt'), mode=mode, encoding='utf-8') as f:
        f.write(text)


def read_update(code):
    root = "./.update"
    with open(os.path.join(root, code + '.log'), mode='r', encoding='utf-8') as f:
        return int(f.read())


def write_update(code, chapter):
    root = "./.update"
    if not os.path.exists(root):
        os.makedirs(root)
    with open(os.path.join(root, code + '.update'), mode='w', encoding='utf-8') as f:
        f.write(str(chapter))


def main():
    global text_dict, _url
    text_dict = {}

    user_input = input('请输入小说编号：')
    code = user_input
    _url = 'https://www.bige7.com/book/' + user_input + '/'

    info = novel_name(_url)
    name = info[0]
    latest_chapter = info[1]
    book_info = info[2]

    user_input = input('你要下载的小说是：《%s》，确定吗？' % name)
    timer = time()

    save_mode = 'w'
    if user_input == 'exit':
        print('好的我退出')
        _text = ''
        exit()
        pass
    elif user_input == '+':  # 更新模式
        save_mode = 'a'
        _text = range_download(read_update(code), latest_chapter)
        write_update(code, latest_chapter)
        pass
    elif user_input == '-':  # 自定义模式
        _start = input("请输入开始位置：")
        _end = input("请输入结束位置：")
        start = int(_start) if _start != '~' else 1
        end = int(_end) if _end != '~' else latest_chapter

        _text = '【自定义下载：' + str(start) + '~' + str(end) + '】\n\n' + range_download(start, end, book_info)
        # 自定义下载如果在开始输入'~'则会设定为1；在结束输入'~'则会设定为目前最后一章
        pass
    else:                    # 普通模式
        _text = range_download(1, latest_chapter, book_info)
        write_update(code, latest_chapter)
        pass

    root = './我滴小说'
    save(root, _text, name, mode=save_mode)
    print('总用时：', str(round(time()-timer, 3)))
    # 自定义模式不写更新信息，其他都写

    return


if __name__ == '__main__':
    main()
    # by 南哥183
