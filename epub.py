# coding: utf-8
import os
import os.path
import re
import zipfile
# from chardet.universaldetector import UniversalDetector
from cchardet import Detector as UniversalDetector
import jinja2
import requests


__author__ = "ZhangDesheng"

__related_links__ = (
    "http://jingyan.baidu.com/album/3ea51489c553db52e61bbaa1.html?picindex=2",
    "http://blog.itpub.net/29733787/viewspace-1477082/",
    )


def get_file_encoding(filename):
    """
    input: filename(str) absolute path of a file 
    output: str
    """
    detector = UniversalDetector()
    with open(filename, "rb") as f:
        for line, content in enumerate(f):
            detector.feed(content)
            if line>100:
                break
            if detector.done:
                break
    detector.close()
    return detector.result


def div_file_to_chapters(filename):
    """
    """
    class Chapter(object):
        def __init__(self, index, title, content):
            self.index = index
            self._title = title
            self._content = content

        @property
        def title(self):
            return self._title

        @property
        def content(self):
            return self._content

        @content.setter
        def content(self, value):
            self._content = value


    chapterList = list()
    encoding = get_file_encoding(filename).get("encoding")
    if encoding.lower() == "gb2312":
        encoding = "gbk"
    reChapter = re.compile(r"(第[\s]*[0-9〇一二三四五六七八九十零壹贰叁肆伍陆柒捌玖拾百佰千仟１２３４５６７８９０]+[\s]*[章节回])[\s]*(.*)")
    last_content_buff = ""
    curr_chapter_index = 0

    # 先登记一章 保存匹配到章节之前的文字
    c = Chapter(curr_chapter_index, "", "")
    chapterList.append(c)
    with open(filename, encoding=encoding) as f:
        for index, line in enumerate(f):
            chapter_match = reChapter.search(line)
            line = line.strip()
            if chapter_match:
                curr_chapter_index += 1
                c = Chapter(curr_chapter_index, chapter_match.group(0).strip(), "")
                chapterList.append(c)                
                chapterList[curr_chapter_index-1].content = last_content_buff
                last_content_buff = ""
            else:
                last_content_buff = "".join([last_content_buff, line])
        
        chapterList[curr_chapter_index].content = last_content_buff

    # 删除空内容的章节
    chapterList_with_no_blank = [c for c in chapterList if "".join([c.title, c.content])]
    return chapterList_with_no_blank


def txt_to_epub(filename, cover_url=None):
    epub_name = os.path.basename(filename).replace(".txt", ".epub")
    save_dir = os.path.dirname(filename)
    # os.chdir(save_dir)
    epub_name = os.path.join(save_dir, epub_name)

    chapterList = div_file_to_chapters(filename)

    with zipfile.ZipFile(epub_name, "w") as epub:
        print("-"*20, "制作epub开始", "-"*20)
        create_mimetype(epub)
        create_container(epub)
        create_stylesheet(epub)
        create_cover(epub, cover_url=cover_url)
        create_ncx(epub, chapterList)
        create_opf(epub, chapterList)
        create_chapters(epub, chapterList)
    print("-"*20, "制作epub完成", "-"*20)
    print("-"*20, "epub保存在{0}".format(os.path.join(save_dir, epub_name)), "-"*20)
    return epub_name



def render_chapter(chapter, chapter_template="static/chapter.html"):
    with open(chapter_template) as f:
        template = jinja2.Template(f.read())
        chapter_str = template.render(title=chapter.title, content=chapter.content)
        return chapter_str


def create_mimetype(epub):
    epub.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)


def create_container(epub):
    container_info = '''<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
         <rootfile full-path="OEBPS/fb.opf" media-type="application/oebps-package+xml"/>
    </rootfiles> 
</container>'''
    epub.writestr('META-INF/container.xml', container_info, compress_type=zipfile.ZIP_STORED)


def create_stylesheet(epub, css_name="static/main.css"):
    with open(css_name) as f:
        css_info = f.read()
    epub.writestr('OEBPS/css/main.css', css_info, compress_type=zipfile.ZIP_STORED)


def create_cover(epub, cover="static/cover.jpg", cover_url=None):
    if cover_url:
        try:
            epub.writestr('OEBPS/images/cover.jpg', requests.get(cover_url).content, compress_type=zipfile.ZIP_STORED)
            return
        except:
            print('指定的封面路径无法下载!使用默认封面')

    with open(cover, "rb") as f:
        epub.writestr('OEBPS/images/cover.jpg', f.read(), compress_type=zipfile.ZIP_STORED)


def create_chapters(epub, chapterList):
    for chapter in chapterList:
        epub.writestr("OEBPS/chapter{}.html".format(chapter.index), render_chapter(chapter), compress_type=zipfile.ZIP_STORED)


def create_ncx(epub, chapterList, ncx_template="static/fb.ncx", **kwargs):
    bookname = kwargs.get("bookname", "")
    author = kwargs.get("author", "")
    with open(ncx_template, encoding="utf-8") as f:
        template = jinja2.Template(f.read())
        ncx_str =  template.render(bookname=bookname, author=author, chapterList=chapterList)
        epub.writestr("OEBPS/fb.ncx", ncx_str, compress_type=zipfile.ZIP_STORED)

def create_opf(epub, chapterList, opf_template="static/fb.opf", **kwargs):
    kwargs.update({"rights":  "请支持正版阅读，实在不能支持时才阅读这个版本，请感恩作者。"})
    # with open(opf_template, encoding="utf-8") as f, open("opftext.opf", "w", encoding="utf-8") as fw:
    with open(opf_template, encoding="utf-8") as f:
        template = jinja2.Template(f.read())
        opf_str = template.render(chapterList=chapterList, **kwargs)
        # fw.write(opf_str)
        epub.writestr("OEBPS/fb.opf", opf_str, compress_type=zipfile.ZIP_STORED)


if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    if len(sys.argv) > 2:
        cover_url = sys.argv[2]
    else:
        cover_url = None

    print("将文件{}转成epub\n".format(filename))
    txt_to_epub(filename, cover_url=cover_url)

