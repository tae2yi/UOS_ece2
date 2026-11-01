"""LAB7 실험 전(예비) 보고서 생성기 — LAB6 예비보고서의 레이아웃(A4, 2단)과 docx 도우미를 그대로 쓴다.

대상: STM32_3(SPI, 과제8~12). MCU 송신·수신과 FPGA SPI 수신·송신 회로, MCU–FPGA·FPGA–FPGA 연결.
그림은 make_figures.py가, 검증 로그는 tools/run_icarus.sh·run_xsim.sh·build_vivado.tcl이 먼저 만든다.

실행: python build_lab7_report.py [커밋 해시]   (python-docx, Pillow 필요)
      커밋 해시를 주면 보고서의 GitHub 주소가 그 커밋을 가리킨다. 생략하면 master.
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
IMG = HERE / 'images'
OUT = HERE / 'LAB7_예비보고서.docx'

FONT = 'Nanum Gothic'
FONT_CODE = 'Consolas'
NAVY = '1F4E78'
PALE = 'EAF2F8'
GRAY = 'D9D9D9'
REPO = 'https://github.com/tae2yi/UOS_ece2'
CODE_COMMIT = sys.argv[1] if len(sys.argv) > 1 else 'master'
UPSTREAM = 'https://github.com/Glaysia/ece2_26_2_2'
UPSTREAM_COMMIT = '1fab83ee3c6bb595c73d7834be143d3865efa92b'
COL_W = 3.22          # 2단 본문 한 단의 사용 폭(inch)
FIG_W = 3.18
CODE_MAX = 63         # 한 단에 들어가는 코드 한 줄의 최대 글자 수(6.4 pt)

# ============================================================ docx helpers
def gh(path, first=None, last=None, tree=False):
    url = f"{REPO}/{'tree' if tree else 'blob'}/{CODE_COMMIT}/{path}"
    return url + (f'#L{first}-L{last}' if first else '')


def add_hyperlink(paragraph, url, text, size=7.0, color='0563C1'):
    r_id = paragraph.part.relate_to(
        url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    link = OxmlElement('w:hyperlink')
    link.set(qn('r:id'), r_id)
    run = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')
    fonts = OxmlElement('w:rFonts')
    for key in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        fonts.set(qn('w:' + key), FONT)
    rpr.append(fonts)
    c = OxmlElement('w:color'); c.set(qn('w:val'), color); rpr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rpr.append(u)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2))); rpr.append(sz)
    run.append(rpr)
    t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve'); run.append(t)
    link.append(run)
    paragraph._p.append(link)


def add_link_line(doc, label, url):
    p = doc.add_paragraph()
    para_fmt(p, before=1, after=5, line=1.0)
    set_font(p.add_run(f'{label}: '), size=7.0, bold=True, color='555555')
    add_hyperlink(p, url, url)
    return p


def set_font(run, name=FONT, size=10.0, bold=False, color='000000', italic=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.get_or_add_rFonts()
    for key in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        fonts.set(qn('w:' + key), name)


def set_style_font(style, name, size, bold=None, color='000000'):
    style.font.name = name
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor.from_string(color)
    fonts = style.element.get_or_add_rPr().get_or_add_rFonts()
    for key in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        fonts.attrib.pop(qn('w:' + key), None)
    for key in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        fonts.set(qn('w:' + key), name)


def para_fmt(p, before=0, after=4, line=1.12, keep_next=False, keep_together=True, align=None):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    pf.keep_together = keep_together
    pf.keep_with_next = keep_next
    pf.widow_control = True
    if align is not None:
        p.alignment = align


def add_text(doc, text, size=10.0, after=4, keep_next=False):
    text = text.replace('‥', '~')
    p = doc.add_paragraph()
    para_fmt(p, after=after, keep_next=keep_next)
    set_font(p.add_run(text), size=size)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f'Heading {level}')
    para_fmt(p, before=10 if level == 1 else 7, after=5 if level == 1 else 3, line=1.0, keep_next=True)
    set_font(p.add_run(text), size=15.0 if level == 1 else 11.5, bold=True)
    return p


def set_cell_width(cell, inches):
    cell.width = Inches(inches)
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn('w:tcW'))
    if tc_w is None:
        tc_w = OxmlElement('w:tcW')
        tc_pr.append(tc_w)
    tc_w.set(qn('w:w'), str(round(inches * 1440)))
    tc_w.set(qn('w:type'), 'dxa')


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn('w:shd'))
    if shd is None:
        shd = OxmlElement('w:shd')
        tc_pr.append(shd)
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)


def table_setup(table, widths):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pr = table._tbl.tblPr
    layout = OxmlElement('w:tblLayout')
    layout.set(qn('w:type'), 'fixed')
    tbl_pr.append(layout)
    tbl_w = tbl_pr.find(qn('w:tblW'))
    if tbl_w is None:
        tbl_w = OxmlElement('w:tblW')
        tbl_pr.append(tbl_w)
    tbl_w.set(qn('w:w'), str(round(sum(widths) * 1440)))
    tbl_w.set(qn('w:type'), 'dxa')
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement('w:' + edge)
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), GRAY)
        borders.append(el)
    tbl_pr.append(borders)
    mar = OxmlElement('w:tblCellMar')
    for side, v in (('top', 45), ('left', 70), ('bottom', 45), ('right', 70)):
        el = OxmlElement('w:' + side)
        el.set(qn('w:w'), str(v))
        el.set(qn('w:type'), 'dxa')
        mar.append(el)
    tbl_pr.append(mar)
    for col, w in zip(table._tbl.tblGrid.findall(qn('w:gridCol')), widths):
        col.set(qn('w:w'), str(round(w * 1440)))


def row_props(row, header=False):
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement('w:cantSplit'))
    if header:
        h = OxmlElement('w:tblHeader')
        h.set(qn('w:val'), 'true')
        tr_pr.append(h)


def spacer(doc, pt=3):
    p = doc.add_paragraph()
    para_fmt(p, after=0, line=1.0)
    p.paragraph_format.space_after = Pt(pt)
    r = p.add_run()
    set_font(r, size=2)
    return p


def add_table(doc, headers, rows, widths, size=7.4, center_first=True, links=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table_setup(table, widths)
    row_props(table.rows[0], header=True)
    for i, txt in enumerate(headers):
        cell = table.rows[0].cells[i]
        set_cell_width(cell, widths[i])
        set_cell_shading(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        para_fmt(p, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_font(p.add_run(txt), size=size + 0.4, bold=True, color='FFFFFF')
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        row_props(table.rows[-1])
        for cidx, value in enumerate(row):
            cell = cells[cidx]
            set_cell_width(cell, widths[cidx])
            set_cell_shading(cell, PALE if ridx % 2 == 0 else 'FFFFFF')
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.CENTER if (cidx == 0 and center_first) else WD_ALIGN_PARAGRAPH.LEFT
            para_fmt(p, after=0, line=1.0, align=align)
            if links and cidx == 0 and links[ridx]:
                add_hyperlink(p, links[ridx], str(value), size=size)
            else:
                set_font(p.add_run(str(value).replace('‥', '~')), size=size, color='222222')
    spacer(doc, 4)
    return table


def add_code(doc, code, size=6.8, link=None, label='GitHub'):
    lines = []
    for line in code.splitlines():
        body = line.lstrip(' ')
        lines.append(' ' * ((len(line) - len(body)) // 2) + body)
    too_long = [l for l in lines if len(l) > CODE_MAX]
    if too_long:
        raise ValueError(f'code line too long for one column: {too_long}')
    code = '\n'.join(lines)
    table = doc.add_table(rows=1, cols=1)
    table_setup(table, [COL_W])
    row_props(table.rows[0])
    cell = table.cell(0, 0)
    set_cell_width(cell, COL_W)
    set_cell_shading(cell, 'F2F2F2')
    p = cell.paragraphs[0]
    para_fmt(p, after=0, line=1.0)
    for i, line in enumerate(code.splitlines()):
        if i:
            p.add_run().add_break()
        set_font(p.add_run(line), name=FONT_CODE, size=size, color='222222')
    if link:
        add_link_line(doc, label, link)
    else:
        spacer(doc, 4)


def add_figure(doc, path, caption, number, width=FIG_W):
    p = doc.add_paragraph()
    para_fmt(p, before=4, after=1, line=1.0, keep_next=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    shape = p.add_run().add_picture(str(path), width=Inches(width))
    docpr = shape._inline.docPr
    docpr.set('title', f'그림 {number}')
    docpr.set('descr', caption)
    cap = doc.add_paragraph(style='Caption')
    para_fmt(cap, after=6, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_font(cap.add_run(f'그림 {number}. {caption}'), size=8.0, bold=True, color='333333')
    return number + 1


def add_page_field(paragraph):
    run = paragraph.add_run()
    set_font(run, size=7.0, color='7F7F7F')
    for tag, attr in (('w:fldChar', 'begin'), ('w:instrText', None), ('w:fldChar', 'separate'),
                      ('w:t', None), ('w:fldChar', 'end')):
        el = OxmlElement(tag)
        if tag == 'w:fldChar':
            el.set(qn('w:fldCharType'), attr)
        elif tag == 'w:instrText':
            el.set(qn('xml:space'), 'preserve')
            el.text = ' PAGE '
        else:
            el.text = '1'
        run._r.append(el)


def column_break(doc):
    p = doc.add_paragraph()
    para_fmt(p, after=0, line=1.0)
    p.add_run().add_break(WD_BREAK.COLUMN)


def page_setup(section, columns):
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = section.right_margin = Cm(1.8)
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.7)
    section.header_distance = section.footer_distance = Cm(0.8)
    cols = section._sectPr.find(qn('w:cols'))
    if cols is None:
        cols = OxmlElement('w:cols')
        section._sectPr.append(cols)
    cols.set(qn('w:num'), str(columns))
    cols.set(qn('w:space'), '425')


def bullets(doc, items, size=9.5):
    for item in items:
        p = doc.add_paragraph()
        para_fmt(p, after=2)
        p.paragraph_format.left_indent = Inches(0.14)
        p.paragraph_format.first_line_indent = Inches(-0.12)
        set_font(p.add_run('· ' + item), size=size)
    spacer(doc, 2)


def log_lines(name, keep):
    text = (HERE / 'logs' / name).read_text(encoding='utf-8', errors='replace')
    return [line.rstrip() for line in text.splitlines() if any(k in line for k in keep)]




# ============================================================ 소스에서 직접 가져오는 코드
ROOT = HERE.parents[2]          # UOS_ece2
LAB = 'lab7'
ROUTINE = f'{LAB}/stm32_lab/Core/Src/ece2_474_routine.c'
HOSTSIM = f'{LAB}/stm32_3_hostsim'
D1, D2, D3 = f'{LAB}/lab7_01_spi_rx', f'{LAB}/lab7_02_spi_tx', f'{LAB}/lab7_03_spi_link'


def src_block(path, first_line, end='}'):
    """path에서 first_line으로 시작하는 줄부터 end로 시작하는 줄까지 (코드, 시작 줄, 끝 줄)"""
    lines = (ROOT / path).read_text(encoding='utf-8').splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith(first_line))
    stop = next(i for i in range(start + 1, len(lines)) if lines[i].startswith(end))
    return '\n'.join(lines[start:stop + 1]), start + 1, stop + 1


def result_text(name):
    return (ROOT / HOSTSIM / 'results' / name).read_text(encoding='utf-8').rstrip()


def pass_line(name):
    """Icarus·xsim 로그에서 PASS 줄"""
    text = (HERE / 'logs' / name).read_text(encoding='utf-8', errors='replace')
    return next(l.strip() for l in text.splitlines() if l.startswith('PASS'))


def files_table(doc, folder, rows):
    add_table(doc, ['파일', '역할'], rows, [1.38, 1.84], size=7.0, center_first=False,
              links=[gh(f'{folder}/{r[0]}') for r in rows])


def src_lines(path, first, end, nth=0):
    """first와 정확히 같은 줄(nth번째)부터 end로 시작하는 첫 줄까지 (코드, 시작 줄, 끝 줄)"""
    lines = (ROOT / path).read_text(encoding='utf-8').splitlines()
    starts = [i for i, l in enumerate(lines) if l.rstrip() == first]
    start = starts[nth]
    stop = next(i for i in range(start + 1, len(lines)) if lines[i].startswith(end))
    return '\n'.join(lines[start:stop + 1]), start + 1, stop + 1


def log_tail(name, keep):
    return [l.rstrip() for l in (HERE / 'logs' / name).read_text(encoding='utf-8').splitlines()
            if l.startswith(keep)]


# ============================================================ build
def build():
    doc = Document()
    page_setup(doc.sections[0], 1)

    set_style_font(doc.styles['Normal'], FONT, 10.0)
    doc.styles['Normal'].paragraph_format.space_after = Pt(4)
    doc.styles['Normal'].paragraph_format.line_spacing = 1.12
    for name, size, bold in (('Title', 25.0, True), ('Subtitle', 12.0, False),
                             ('Heading 1', 15.0, True), ('Heading 2', 11.5, True), ('Caption', 8.0, True)):
        set_style_font(doc.styles[name], FONT, size, bold, '333333' if name == 'Caption' else '000000')
    title_ppr = doc.styles['Title'].element.pPr
    if title_ppr is not None and title_ppr.find(qn('w:pBdr')) is not None:
        title_ppr.remove(title_ppr.find(qn('w:pBdr')))

    # ---- cover
    p = doc.add_paragraph(style='Title')
    para_fmt(p, before=150, after=10, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_font(p.add_run('LAB7 예비 보고서'), size=25.0)
    p = doc.add_paragraph(style='Subtitle')
    para_fmt(p, after=34, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_font(p.add_run('STM32_3 SPI — MCU·FPGA 사이의 송수신'), size=12.0, italic=True)
    for key, value in (('과목', '전자전기컴퓨터설계실험 2'), ('제출일', '2026년 11월 2일'),
                       ('성명', '김태이'), ('학번', '2023440158')):
        p = doc.add_paragraph()
        para_fmt(p, after=7, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_font(p.add_run(f'{key}  {value}'), size=10.0)

    body = doc.add_section(WD_SECTION.NEW_PAGE)
    page_setup(body, 2)
    for sec in doc.sections:
        sec.footer.is_linked_to_previous = False
        fp = sec.footer.paragraphs[0]
        para_fmt(fp, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_font(fp.add_run('LAB7 실험 전 보고서  ·  '), size=7.0, color='7F7F7F')
        add_page_field(fp)

    fig = 1
    logs = f'{LAB}/report/pre/logs'

    # ---- 1 범위와 결론
    add_heading(doc, '1 보고서 범위와 결론', 1)
    add_text(doc, '11월 2일 실험(STM32_3)은 SPI 하나에 집중한다. MCU의 SPI1로 한 바이트를 보내 파형을 보고(과제8), MCU 두 대 사이에서 '
                  '주고받은 뒤(과제9), FPGA에 SPI 수신 회로(과제10)와 송신 회로(과제11)를 직접 만들어 MCU와 잇고, 마지막으로 FPGA '
                  '두 대를 연결한다(과제12). 형식은 Mode 0, 8비트, 높은 비트 먼저이고 MISO는 쓰지 않는다. FPGA Verilog는 제공되지 않으므로 '
                  '수신·송신 회로를 처음부터 설계했다.')
    add_text(doc, 'MCU 코드는 한 파일에 쓰고 매크로 STM32_3_ROLE로 송신(마스터)과 수신(슬레이브)을 골라 Arm GCC로 빌드했다. 같은 소스를 PC에서 '
                  '실행하는 호스트 시뮬레이션이 송신 바이트를 파일로 남기면 FPGA 수신 테스트벤치가 그 파일을 MCU와 같은 타이밍의 SPI 신호로 '
                  '넣고, 반대로 FPGA 송신 테스트벤치가 MOSI에서 읽은 바이트를 MCU 수신 코드가 받는다. 네 가지 연결(과제9~12)을 모두 '
                  '코드 수준에서 이어 본 셈이다.')
    add_text(doc, 'FPGA는 수신 회로(spi_rx_uart)와 송신 회로(spi_tx_uart) 두 bitstream을 만들었다. 둘 다 50 MHz에서 타이밍 여유가 '
                  '14 ns 이상이다. FPGA–FPGA 연결은 두 보드의 클록을 일부러 다르게 두고(0.25 % 차이) 선 지연을 넣은 테스트벤치로 확인했다.')
    column_break(doc)
    add_table(doc, ['과제', '사전 검증', '결과'], [
        ['8', 'Arm GCC 빌드, 호스트 8바이트', '55 A5 00 FF, 비트 순서 일치'],
        ['9', '호스트 마스터 → 슬레이브', 'RX 8줄 일치, 타임아웃 문구'],
        ['10', 'MCU 파일 → FPGA TB', 'UART 9줄·LED 일치, 끊긴 바이트 복구'],
        ['11', 'FPGA TB → MCU 호스트', 'SCK 500 kHz, RX 8줄 일치'],
        ['12', '보드 두 대 TB', '클록이 달라도 8바이트 일치'],
        ['구현', '두 설계 bitstream', 'WNS +14.349 / +15.484 ns'],
    ], [0.42, 1.4, 1.4], size=7.0)
    add_text(doc, 'PASS와 호스트 시뮬레이션 결과는 논리가 맞다는 뜻이다. 실제 선의 파형(울림, 지연), MCU HAL 함수가 CS와 SCK 사이에 넣는 '
                  '시간, 점퍼선 결선, 보드 클록 스위치 상태는 포함하지 않으므로 각 장 끝의 표대로 오실로스코프와 보드에서 확인한다.',
             size=8.5)

    # ---- 2 환경
    add_heading(doc, '2 실험 환경과 검증 방법', 1)
    add_table(doc, ['구분', '사용한 것'], [
        ['MCU 보드', 'NUCLEO-G474RE (STM32G474RE, Cortex-M4)'],
        ['MCU 프로젝트', 'Glaysia/ece2_26_2_2의 c/stm32/base'],
        ['MCU 빌드', 'Arm GNU Toolchain 13.3.Rel1, CMake 3.24.2, Ninja 1.11.1'],
        ['호스트 검증', 'MinGW-W64 gcc 9.5.0, HAL 대역 헤더'],
        ['FPGA 보드', 'Combo II-DLD, xc7s75fgga484-1'],
        ['FPGA 도구', 'Vivado 2025.2, Icarus Verilog 12.0'],
        ['계측', '오실로스코프(SCK·MOSI·CS), Serial Monitor 2개'],
    ], [0.92, 2.30], size=7.0)
    add_text(doc, '조교 저장소가 이번 주에 ece2_26_2_2로 옮겨졌다. 새 저장소의 기본 프로젝트(c/stm32/base)는 LAB6까지 쓴 프로젝트와 파일이 '
                  '같고, ece2_474_routine.c도 원본과 한 글자도 다르지 않음을 diff로 확인했다. 그래서 LAB6 폴더를 lab7/stm32_lab으로 복사한 뒤 '
                  'ece2_474_routine.c만 원본으로 되돌리고 이번 과제를 작성했다. 매뉴얼의 SPI 제공 코드 파일(08_spi_master, 09_spi_slave)은 '
                  'stm32_lab/docs/examples에 함께 두었다.')
    add_text(doc, '빌드는 세 가지다. 기본(Debug 프리셋)은 송신 측으로 0x55, 0xA5, 0x00, 0xFF를 1초마다 차례로 보낸다. '
                  '-DSTM32_3_TX_FIXED=0x55를 주면 한 값만 계속 보내 오실로스코프로 보기 쉽고, -DSTM32_3_ROLE=2를 주면 수신 측이 된다.')
    add_text(doc, '호스트 시뮬레이션은 LAB6의 HAL 대역에 SPI 함수(Init, DeInit, Transmit, Receive)와 GPIO_Init을 더했다. HAL_GetTick은 1 ms씩 '
                  '늘어나는 가상 시각이다. 송신 대역은 보낸 바이트를 파일에 적고, 같은 바이트를 Mode 0 규칙대로 SCK·MOSI·CS 시각표(CSV)로 펼친 뒤 '
                  '상승 에지에서 다시 읽어 원래 값이 나오는지 확인한다. 수신 대역은 init이 SPI1을 슬레이브·NSS 하드웨어 입력으로 바꾸고 PA4를 '
                  'AF5로 설정했을 때만 파일의 바이트를 돌려준다.')
    add_text(doc, 'FPGA는 프로젝트마다 기능 검사용 tb.sv와 파형 확인용 tb_view.sv를 직접 작성해 Icarus와 Vivado 시뮬레이터에서 실행했다. '
                  'Vivado 파형 캡처는 한 단 폭에서 읽히도록 시간축을 반으로 잘라 두 줄로 배치했다.')

    # ---- 3 출처
    add_heading(doc, '3 소스 출처와 실행 스냅샷', 1)
    add_table(doc, ['항목', '식별 정보'], [
        ['MCU 템플릿', f'{UPSTREAM}.git (c/stm32/base)'],
        ['커밋', UPSTREAM_COMMIT],
        ['FPGA 템플릿', 'fpga-lab-template v2.0.2 (같은 저장소 templates/fpga)'],
        ['FPGA 코드', '직접 작성. uart_tx만 LAB3-07(lab6_04_uart_led)과 같음'],
        ['제출 저장소', REPO],
        ['LAB7 코드', f'{CODE_COMMIT} (보고서의 GitHub 주소가 가리키는 위치)'],
        ['폴더', 'lab7/stm32_lab, stm32_3_hostsim, lab7_01_spi_rx, lab7_02_spi_tx, lab7_03_spi_link'],
    ], [0.9, 2.32], size=7.0)
    add_link_line(doc, 'GitHub', gh(LAB, tree=True))
    add_text(doc, '템플릿에서 바꾼 MCU 파일은 Core/Src/ece2_474_routine.c 하나다. 원본 대비 바뀐 내용 전체는 아래 diff에 있다. 호스트 '
                  '시뮬레이션의 입력·출력, FPGA 시뮬레이션 로그, Vivado 리포트도 같은 저장소에 있다.')
    add_link_line(doc, 'diff', gh(f'{logs}/stm32_routine.diff'))

    # ================================================================= SPI 개요
    add_heading(doc, 'STM32_3 SPI 통신', 1)
    add_heading(doc, '신호와 Mode 0', 2)
    add_text(doc, 'SPI는 클록 선을 따로 두는 동기식 직렬 통신이다. 마스터가 SCK를 만들고 MOSI로 데이터를 내보내며, CS(칩 선택)를 LOW로 '
                  '내려 통신할 슬레이브를 고른다. 슬레이브는 받은 SCK의 에지에 맞춰 MOSI를 읽으므로, UART처럼 양쪽이 속도를 미리 약속할 '
                  '필요가 없다. 대신 선이 하나 더 필요하다[2]. 슬레이브가 마스터로 보내는 MISO 선도 있지만 이번 실습은 한 방향씩만 보므로 '
                  '연결하지 않는다.')
    add_text(doc, 'Mode는 클록 극성(CPOL)과 위상(CPHA)의 조합이다. Mode 0(CPOL=0, CPHA=0)은 SCK가 쉬는 동안 LOW이고, 첫 에지인 상승 '
                  '에지에서 읽는다. 따라서 보내는 쪽은 첫 상승 에지 전에 첫 비트(bit7)를 내놓고, 하강 에지마다 다음 비트로 바꾼다. 읽는 '
                  '순간에 MOSI가 반주기 동안 안정되어 있는 구조다. main.c의 설정이 이와 같다(CLKPolarity LOW, CLKPhase 1EDGE, FirstBit MSB).')
    fig = add_figure(doc, IMG / 'theory' / 'spi_mode0.png',
                     'MCU 호스트 시뮬레이션이 만든 0x55·0xA5의 SCK·MOSI·CS 시각표. 초록 숫자는 상승 에지에서 읽은 비트다.', fig)
    add_text(doc, '0x55를 높은 비트부터 읽으면 0 1 0 1 0 1 0 1, 0xA5는 1 0 1 0 0 1 0 1이다. 0x55는 비트가 매번 바뀌므로 MOSI가 SCK의 '
                  '절반 주파수로 토글하고, 0x00과 0xFF는 MOSI가 내내 LOW 또는 HIGH라 비트 경계가 보이지 않는다. 이때는 SCK 상승 에지 8번으로 '
                  '바이트 길이를 확인한다.')
    add_heading(doc, 'SCK 주파수', 2)
    add_text(doc, 'SPI1은 APB2 클록을 쓴다. main.c에서 HSI 16 MHz를 PLL로 ÷2 ×25 ÷2 하여 시스템 클록 100 MHz를 만들고 APB2 분주는 1이다. '
                  '분주비가 128이므로 SCK = 100 MHz / 128 = 781.25 kHz, 주기 1.28 µs이고 한 바이트(8비트)는 10.24 µs다. FPGA 마스터는 '
                  '50 MHz를 100으로 나눠 500 kHz(주기 2 µs)로 만들어 매뉴얼의 1 MHz 이하 조건을 지킨다.')
    add_table(doc, ['쪽', '분주', 'SCK', '1바이트'], [
        ['MCU SPI1 마스터', '100 MHz / 128', '781.25 kHz', '10.24 µs'],
        ['FPGA spi_master_tx', '50 MHz / (2×50)', '500 kHz', '16 µs'],
    ], [1.0, 0.95, 0.67, 0.6], size=7.0)
    add_heading(doc, '코드 읽기 항목', 2)
    add_table(doc, ['표현', '뜻'], [
        ['SPI_HandleTypeDef', 'SPI 설정·상태를 묶은 구조체. hspi1은 그 변수'],
        ['hspi1.Init.Mode', '구조체 안의 설정 항목. 점(.)으로 접근'],
        ['HAL_SPI_Transmit(&hspi1, &tx, 1U, 100U)', '1바이트 송신, 최대 100 ms 대기'],
        ['HAL_SPI_Receive(…, 2000U)', '1바이트 수신, 최대 2 s 대기'],
        ['SPI_NSS_HARD_INPUT', 'NSS(PA4) 핀으로 선택 신호를 받음'],
        ['GPIO_AF5_SPI1', 'PA4를 SPI1의 대체 기능으로 연결'],
        ['%02X', '최소 두 자리 대문자 16진수'],
    ], [1.42, 1.8], size=6.8, center_first=False)
    add_text(doc, 'HAL_SPI_Transmit은 바이트를 송신 FIFO에 넣고 전송이 끝날 때까지 기다린 뒤 돌아온다[1]. 결과 HAL_OK(0)는 MCU 쪽 송신이 '
                  '끝났다는 뜻일 뿐이고, MISO를 쓰지 않으므로 상대가 받았는지는 알 수 없다. 받았는지는 수신 측의 출력으로만 확인한다.')
    add_heading(doc, '전기적 연결과 주의', 2)
    add_text(doc, 'STM32G474와 Combo II-DLD의 FPGA I/O는 모두 3.3 V 논리라 점퍼선으로 바로 잇는다. FPGA 쪽은 LAB6과 같이 브레드보드 '
                  'I/O의 BDIO_0~2(F8, E8, A7)를 SCK, MOSI, CS에 쓰고 GND는 옆 헤더 J6에 잇는다. 이 핀들은 버스 스위치와 100 Ω 직렬 저항을 '
                  '거치며 DIP 스위치 SW5(BD_SEL)를 켜야 FPGA와 이어진다. 두 장치의 GND는 반드시 함께 묶는다.')
    add_text(doc, '한 선에 출력이 둘 이상 붙지 않게 하는 것이 가장 중요하다. MCU가 송신 프로그램인 채로 FPGA 송신 회로에 연결하면 PB3·PA7과 '
                  'F8·E8이 서로 반대 값을 낼 수 있다. 그래서 받는 쪽에 수신 프로그램(또는 수신 bitstream)을 먼저 올린 다음 선을 잇고, '
                  '역할을 바꿀 때도 프로그램을 먼저 바꾼다.')
    fig = add_figure(doc, IMG / 'block' / 'spi_wiring.png',
                     '과제9~12의 연결. 왼쪽이 송신(마스터), 오른쪽이 수신이다. MCU 수신 측의 CS는 PB6가 아니라 PA4(NSS)로 받는다.', fig)

    # ================================================================= 과제8
    add_heading(doc, 'STM32_3 과제8 MCU 송신 파형 확인', 1)
    add_heading(doc, '요구 조건과 설계', 2)
    bullets(doc, ['1초마다 한 바이트를 SPI1로 보내고, 보낸 값과 결과를 VCP UART에 출력한다.',
                  '오실로스코프로 SCK·MOSI·CS를 보고 비트 순서와 SCK 주파수를 기록한다.',
                  '보내는 값을 0x55, 0xA5, 0x00, 0xFF로 바꿔 비교한다.'])
    add_text(doc, '매뉴얼의 송신 예제는 0x55 한 값만 보낸다. 값을 바꿀 때마다 다시 빌드하지 않도록 네 값을 배열에 두고 1초마다 차례로 보내게 '
                  '했다. 한 값만 계속 봐야 할 때는 STM32_3_TX_FIXED 매크로로 고정한다. 1초 간격은 HAL_GetTick()의 차이로 재므로 '
                  'polling_routine이 기다리지 않고 바로 돌아간다. CS(PB6)는 main.c가 처음에 HIGH로 두고, 보낼 때만 LOW로 내렸다가 올린다.')
    add_heading(doc, '핵심 코드', 2)
    code, a, b = src_lines(ROUTINE, 'void polling_routine(void)', '}')
    add_code(doc, code, size=6.0, link=gh(ROUTINE, a, b))
    add_text(doc, '#if STM32_3_ROLE == 1 쪽이 송신이다. 마지막 바이트를 보낸 뒤 index가 0으로 돌아가도록 나머지 연산을 쓰고, 배열 길이는 '
                  'sizeof로 구해 값을 늘려도 코드를 고칠 필요가 없게 했다. ece2_474_init()은 송신 측에서 비워 둔다. 기본 SPI1 설정이 '
                  '이미 마스터·Mode 0이기 때문이다.')
    add_heading(doc, '예상 결과', 2)
    add_text(doc, '호스트 시뮬레이션으로 8.5초 동안 실행한 VCP 출력과, 같은 바이트를 시각표로 펼쳐 상승 에지에서 다시 읽은 결과다.')
    run = [l for l in result_text('run.log').splitlines() if l.startswith('t=')][:4]
    add_code(doc, '\n'.join(['$ master 8   (VCP 출력)', result_text('master_vcp.txt').replace('\r', ''),
                             '$ 시각표 확인(앞 4바이트)'] +
                            [l.replace('  MOSI bits(MSB first) ', ' ').replace('rising-edge decode ', '-> ') for l in run]),
             size=6.0, link=gh(f'{HOSTSIM}/results', tree=True), label='결과')
    add_table(doc, ['값', 'MOSI(상승 에지 순서)', '오실로스코프에서'], [
        ['0x55', '0 1 0 1 0 1 0 1', 'SCK 절반 주파수로 토글'],
        ['0xA5', '1 0 1 0 0 1 0 1', '가운데 두 비트 0 0'],
        ['0x00', '0 0 0 0 0 0 0 0', 'MOSI LOW 고정'],
        ['0xFF', '1 1 1 1 1 1 1 1', 'MOSI HIGH 고정'],
    ], [0.5, 1.22, 1.5], size=7.0)
    add_text(doc, 'CS가 LOW인 시간은 8비트 10.24 µs에 HAL 함수의 처리 시간이 더해진 값이다. HAL_GPIO_WritePin과 HAL_SPI_Transmit 진입 사이, '
                  '전송이 끝난 뒤 CS를 올리기까지 각각 수 µs가 걸릴 것으로 보지만 정확한 값은 코드만으로 정할 수 없어 오실로스코프로 잰다.')
    add_heading(doc, '빌드 결과와 보드에서 확인할 항목', 2)
    add_code(doc, '\n'.join(['$ cmake --preset Debug && cmake --build --preset Debug',
                             'RAM:    2648 B / 128 KB  (2.02 %)', 'FLASH: 28924 B / 512 KB  (5.52 %)',
                             '$ ... -DSTM32_3_TX_FIXED=0x55    FLASH 28892 B',
                             '$ ... -DSTM32_3_ROLE=2           FLASH 30764 B',
                             '경고 0개 (세 빌드 모두)']), size=6.2,
             link=gh(f'{logs}/stm32_arm_build.txt'), label='로그')
    add_table(doc, ['확인 항목', '예상 관찰'], [
        ['VCP(9600)', '1초마다 TX=55, result=0 → A5 → 00 → FF'],
        ['CS(PB6)', '평소 HIGH, 1초마다 약 10 µs 이상 LOW'],
        ['SCK(PB3)', 'CS LOW 동안 상승 에지 8번, 대기 LOW'],
        ['SCK 주기', '1.28 µs = 781.25 kHz'],
        ['MOSI(PA7)', '위 표의 비트열, 하강 에지에서 바뀜'],
        ['CS↓ → 첫 SCK↑', '시간 기록(HAL 처리 시간)'],
    ], [0.95, 2.27], size=7.0)

    # ================================================================= 과제9
    add_heading(doc, 'STM32_3 과제9 MCU → MCU 수신 확인', 1)
    add_heading(doc, '수신 측 설정', 2)
    add_text(doc, '수신 MCU는 main.c와 CubeMX를 고치지 않고 ece2_474_init()에서 SPI1을 다시 설정한다. 먼저 HAL_SPI_DeInit으로 마스터 설정을 '
                  '풀고, Mode를 슬레이브로, NSS를 하드웨어 입력으로 바꿔 다시 초기화한 뒤 PA4를 SPI1의 NSS 기능(AF5)으로 연결한다. 송신 측의 '
                  'CS는 일반 GPIO PB6이지만 수신 측은 SPI 하드웨어가 직접 읽는 PA4로 받아야 한다. 풀업을 켜서 선이 빠져도 선택되지 않은 '
                  '상태(HIGH)로 둔다.')
    code, a, b = src_lines(ROUTINE, '#if STM32_3_ROLE == 2', '#endif')
    add_code(doc, code, size=6.0, link=gh(ROUTINE, a, b))
    add_text(doc, '수신 측 polling_routine은 앞 코드의 #else 쪽이다. HAL_SPI_Receive로 최대 2초 기다리고, 받으면 RX=값, 시간이 지나면 '
                  '배선을 확인하라는 문구를 출력한다. 송신 측이 1초마다 보내므로 정상이면 타임아웃이 나오지 않는다.')
    add_heading(doc, '예상 결과', 2)
    add_text(doc, '송신 측 호스트 시뮬레이션이 보낸 8바이트를 수신 측에 넣은 결과와, 중간에 2초 동안 아무것도 오지 않은 경우의 결과다.')
    add_code(doc, '\n'.join(['$ slave < master_spi.hex', result_text('slave_from_mcu_vcp.txt').replace('\r', ''),
                             '$ slave < 55, (2초 없음), A5', result_text('slave_timeout_vcp.txt').replace('\r', '')]),
             size=6.0, link=gh(f'{HOSTSIM}/results', tree=True), label='결과')
    add_text(doc, '수신 측을 먼저 실행해야 한다. 송신 측이 바이트를 보내는 도중에 수신 측이 시작하면 첫 바이트의 일부 비트를 놓쳐 값이 '
                  '밀릴 수 있다(예: 0x55가 0xAA처럼 보임). 그런 값이 나오면 송신 측을 멈추고 수신 측을 리셋한 뒤 다시 시작한다.')
    add_heading(doc, '역할 교대와 보드에서 확인할 항목', 2)
    add_text(doc, '앞 조가 송신·뒤 조가 수신으로 먼저 하고 바꾼다. 바꿀 때는 프로그램만이 아니라 CS 선도 새 송신 측의 PB6 → 새 수신 측의 PA4로 '
                  '옮긴다. SCK(PB3)와 MOSI(PA7)는 양쪽이 같은 핀이라 그대로 둔다.')
    add_table(doc, ['확인 항목', '예상 관찰'], [
        ['수신 측만 실행', '2초마다 RX timeout 문구(정상 대기)'],
        ['송신 측 실행', '수신 VCP에 RX=55, A5, 00, FF 반복'],
        ['송신·수신 출력 비교', '같은 순서, 같은 값'],
        ['GND 선 제거', '값이 틀리거나 타임아웃(비교용)'],
        ['역할 교대', 'CS 선 PB6 → PA4 다시 연결 후 같은 결과'],
    ], [1.05, 2.17], size=7.0)

    # ================================================================= 과제10
    add_heading(doc, 'STM32_3 과제10 MCU → FPGA 수신 구현', 1)
    add_heading(doc, '목적과 원리', 2)
    add_text(doc, 'FPGA가 SPI 슬레이브가 되어 MCU가 보낸 바이트를 받고, 그 값을 보드의 USB-UART로 PC에 보내 MCU의 송신값과 비교한다. '
                  'FPGA 안에는 50 MHz 클록이 따로 있으므로 SCK를 클록으로 쓰지 않고 입력 신호로 취급한다. SCK·MOSI·CS를 50 MHz 클록에 '
                  '맞춰 받은 뒤, SCK의 이전 값과 현재 값을 비교해 상승 에지를 찾는다.')
    add_text(doc, '외부 신호는 FPGA 클록과 관계없이 바뀌므로 플립플롭의 준비 시간을 어길 수 있고, 그러면 출력이 잠시 0도 1도 아닌 상태(메타안정)에 '
                  '머문다. 플립플롭 두 개를 이어 한 클록 동안 안정될 시간을 주는 것이 2단 동기화다[2]. 세 신호가 같은 2클록 지연을 거치므로 '
                  '동기화된 SCK의 상승 에지에서 읽은 MOSI는 실제 상승 에지 때의 값과 같다.')
    add_text(doc, 'MCU의 SCK 반주기는 640 ns = 32클록이고 MOSI는 하강 에지에서만 바뀐다. 동기화와 에지 검출에 걸리는 3클록(60 ns)은 반주기에 '
                  '비해 매우 짧아 읽는 순간 MOSI가 바뀔 위험이 없다. 이 방식은 SCK의 HIGH·LOW가 각각 2클록 이상이어야 하므로 이론상 '
                  'SCK 12.5 MHz 미만에서 동작하며, 이번 0.78 MHz와 0.5 MHz는 여유가 크다.')
    fig = add_figure(doc, IMG / 'block' / '01_spi_rx_block.png',
                     'FPGA 수신 회로(spi_rx_uart). 동기화 → 에지 검출·시프트 → 바이트 완성 → UART 한 줄 출력과 LED.', fig)
    add_heading(doc, '핵심 코드', 2)
    code, a, b = src_lines(f'{D1}/src/spi_slave_rx.v', '    always @(posedge clk) begin', '    end')
    add_code(doc, code, size=6.0, link=gh(f'{D1}/src/spi_slave_rx.v', a, b))
    add_text(doc, 'CS가 LOW인 동안 상승 에지마다 MOSI를 시프트 레지스터 오른쪽에 넣으므로 먼저 온 bit7이 왼쪽 끝으로 밀려 올라간다. 7비트를 '
                  '모은 뒤 8번째 에지에서 {shift, mosi_s}로 한 바이트를 만들고 valid를 한 클록 낸다. CS가 HIGH가 되면 bit_count를 0으로 '
                  '돌리므로, 중간에 끊긴 바이트가 있어도 다음 바이트는 처음부터 받는다.')
    add_text(doc, '받은 값은 hex_line_tx가 MCU 출력과 같은 모양의 "RX=55" + CR LF 7글자로 바꿔 uart_tx(LAB3-07과 같은 9600 8N1)로 보낸다. '
                  '16진수 한 자리는 0~9면 0x30을, A~F면 0x37을 더해 ASCII로 만든다. 한 줄은 7.3 ms라 1초 간격의 바이트를 놓치지 않는다. '
                  '7.3 ms 안에 바이트가 또 오면 그 줄은 건너뛰지만 LED에는 표시된다.')
    files_table(doc, D1, [['src/spi_slave_rx.v', '동기화, 에지 검출, 8비트 수신'],
                          ['src/hex_line_tx.v', '바이트를 "RX=55" 줄로 UART 출력'],
                          ['src/uart_tx.v', 'UART 송신 8N1(LAB3-07)'],
                          ['src/spi_rx_uart.v', '설계 top. LED = 마지막 바이트'],
                          ['sim/tb.sv', 'MCU 호스트 출력 파일로 검사'],
                          ['sim/tb_view.sv', '파형 확인용. 0x55, 0xA5'],
                          ['constraints/spi_rx_uart.xdc', 'BDIO_0~2 입력, F6, LED']])
    add_heading(doc, '시뮬레이션 결과', 2)
    add_text(doc, 'tb.sv는 MCU 호스트 시뮬레이션이 보낸 8바이트(sim/mcu_spi.hex)를 MCU와 같은 781.25 kHz SPI 신호로 넣는다. CS를 내린 뒤 첫 '
                  '에지까지 3 µs, 마지막 에지 뒤 CS를 올리기까지 2 µs를 두었다. UART는 실제 9600 bps로 받아 줄마다 비교한다. 마지막에는 '
                  '4비트만 보내고 CS를 올린 뒤 0x3C를 보내, 끊긴 바이트 뒤에도 0x3C를 받는지 본다. 바이트 간격만 1초 대신 10 ms로 줄였다.')
    add_code(doc, '\n'.join([l.replace('UART line', 'line') for l in log_tail('lab7_01_spi_rx_tb_icarus.txt', 't=')] +
                            ['[Icarus·Vivado] PASS: 9 bytes, UART lines and LED match,',
                             '                partial-byte recovery 0x3C']), size=6.0,
             link=gh(f'{logs}/lab7_01_spi_rx_tb_icarus.txt'), label='로그')
    fig = add_figure(doc, IMG / 'vivado' / 'lab7_01_spi_rx_tb_view.png',
                     'FPGA 수신 Vivado 파형(tb_view, UART 1 Mbps). sck_rise마다 bit_count가 0→7로 늘고 8번째 에지에서 rx_valid와 rx_data(55, a5)가 '
                     '나온 뒤 txd로 "RX=" 줄이 나간다.', fig)
    add_text(doc, 'cs_n_s와 sck_s는 원래 신호보다 2클록(40 ns) 늦다. shift가 0101010까지 모인 상태에서 8번째 에지가 오면 rx_data가 55가 '
                  '되고, CS가 HIGH인 동안 bit_count는 0에 머문다. 두 번째 바이트 0xA5도 같은 방법으로 받아 rx_data가 a5로 바뀐다.')
    fig = add_figure(doc, IMG / 'vivado' / 'lab7_01_spi_rx_tb.png',
                     'FPGA 수신 Vivado 전체 파형(tb, 약 90 ms). 10 ms마다 바이트가 들어와 rx_valid 뒤 7.3 ms 동안 txd로 한 줄이 나가고, '
                     'n_lines가 9까지 는다.', fig)
    add_heading(doc, '구현 결과와 보드에서 확인할 항목', 2)
    add_table(doc, ['신호', '핀', '연결'], [
        ['spi_sck', 'F8 (BDIO_0)', 'MCU PB3, 풀다운'],
        ['spi_mosi', 'E8 (BDIO_1)', 'MCU PA7, 풀다운'],
        ['spi_cs_n', 'A7 (BDIO_2)', 'MCU PB6, 풀업'],
        ['uart_txd', 'F6', 'USB-UART → PC'],
        ['led[7:0]', 'L4 M4 M2 N7 M7 M3 M1 N5', 'LED1(bit7)~LED8'],
    ], [0.75, 1.25, 1.22], size=7.0, center_first=False)
    add_text(doc, '입력에는 내부 풀업·풀다운을 켜서 선이 빠져도 SCK LOW, CS HIGH(선택 안 됨)로 보이게 했다. 잡음이 에지로 읽혀 엉뚱한 바이트가 '
                  '출력되는 것을 막는다.')
    add_table(doc, ['항목', '값'], [
        ['LUT · 레지스터', '88개 · 99개'],
        ['타이밍', '50 MHz에서 WNS +14.349 ns, 위반 없음'],
        ['DRC', '오류 0, 경고 1 (CFGBVS 미설정)'],
        ['bitstream', 'lab7_01_spi_rx/bitstream/spi_rx_uart.bit'],
    ], [0.9, 2.32], size=7.2)
    add_link_line(doc, 'XDC', gh(f'{D1}/constraints/spi_rx_uart.xdc'))
    add_table(doc, ['확인 항목', '예상 관찰'], [
        ['준비', 'SW5 켬, 클록 스위치 F(50 MHz), SW1 리셋'],
        ['FPGA COM(9600)', '1초마다 RX=55, A5, 00, FF'],
        ['MCU VCP', 'TX=값과 FPGA 출력이 같은 순서'],
        ['LED (0x55)', 'LED1 꺼짐부터 꺼짐·켜짐 번갈아'],
        ['LED (0xA5)', '켜짐 꺼짐 켜짐 꺼짐 꺼짐 켜짐 꺼짐 켜짐'],
        ['CS 선 제거', '출력 멈춤(풀업으로 선택 안 됨)'],
    ], [0.95, 2.27], size=7.0)

    # ================================================================= 과제11
    add_heading(doc, 'STM32_3 과제11 FPGA → MCU 송신 구현', 1)
    add_heading(doc, '목적과 설계', 2)
    add_text(doc, 'FPGA가 마스터가 되어 SCK, MOSI, CS를 직접 만든다. 1초마다 0x55, 0xA5, 0x00, 0xFF를 차례로 보내 MCU 송신 예제와 같은 값을 '
                  '비교할 수 있게 했다. DIP 스위치로 값을 고르는 방법도 생각했지만, BDIO 연결에 DIP 스위치 SW5를 쓰므로 혼동을 피하려고 '
                  '정해진 순서로 보낸다. 보낸 값은 FPGA UART로 "TX=55"처럼 PC에 알리고 LED에도 표시한다.')
    fig = add_figure(doc, IMG / 'block' / '02_spi_tx_block.png',
                     'FPGA 송신 회로(spi_tx_uart). 1초 타이머가 다음 값을 골라 spi_master_tx를 시작하고, 끝나면(done) UART와 LED에 표시한다.', fig)
    add_text(doc, 'spi_master_tx는 반주기(HALF = 50클록 = 1 µs)마다 한 단계씩 움직이는 상태 기계다. CS를 내리면서 bit7을 MOSI에 내놓고(LEAD), '
                  'SCK를 올렸다 내리기를 8번 반복하며 내릴 때마다 다음 비트를 내놓는다(HIGH, LOW). 8번째 하강 에지 뒤 반주기 기다려 CS를 '
                  '올리고(TRAIL), 다시 반주기 쉰다(GAP). SCK·MOSI·CS 모두 플립플롭에서 바로 나가므로 조합 논리의 글리치가 선에 실리지 않는다.')
    fig = add_figure(doc, IMG / 'theory' / 'spi_master_states.png',
                     '0xA5를 보낼 때 spi_master_tx의 상태 순서. CS LOW는 LEAD 1 + 비트 15반주기 + TRAIL 1 = 17 µs다.', fig)
    add_heading(doc, '핵심 코드', 2)
    code, a, b = src_lines(f'{D2}/src/spi_master_tx.v', '    always @(posedge clk) begin', '    end')
    add_code(doc, code, size=6.0, link=gh(f'{D2}/src/spi_master_tx.v', a, b))
    add_text(doc, 'count는 상태에 들어갈 때 HALF−1로 두고 0이 될 때까지 줄이므로 각 상태는 정확히 50클록이다. HIGH에서 SCK를 내리는 클록에 '
                  'mosi <= shift[6]으로 다음 비트를 내고 shift를 왼쪽으로 민다. 수신 측은 그 뒤 반주기(1 µs) 동안 안정된 값을 상승 에지에서 '
                  '읽는다.')
    files_table(doc, D2, [['src/spi_master_tx.v', 'Mode 0 마스터 상태 기계'],
                          ['src/spi_tx_uart.v', '설계 top. 1초 타이머, 값 순서'],
                          ['src/hex_line_tx.v, uart_tx.v', '"TX=55" 줄 출력(01과 같음)'],
                          ['sim/tb.sv', 'SPI 수신 모델로 타이밍·값 검사'],
                          ['sim/tb_view.sv', '파형 확인용. 0x55, 0xA5'],
                          ['constraints/spi_tx_uart.xdc', 'BDIO_0~2 출력, F6, LED']])
    add_heading(doc, '시뮬레이션 결과', 2)
    add_text(doc, 'tb.sv 안에 오실로스코프와 MCU 수신 측 역할을 하는 SPI 수신 모델을 두었다. 바이트마다 CS LOW 동안 상승 에지가 정확히 8번인지, '
                  'SCK 주기가 2000 ns인지, CS↓에서 첫 상승 에지까지 1000 ns인지, SCK가 HIGH인 동안 MOSI가 바뀌지 않는지, 읽은 값이 순서대로 '
                  '맞는지 검사한다. 송신 간격만 10 ms로 줄였다. 읽은 바이트는 파일로 남겨 MCU 수신 호스트 시뮬레이션에 넣었다.')
    add_code(doc, '\n'.join([l.replace(' (8 edges, period 2000 ns, CS->SCK 1000 ns)', '  8 edges OK')
                             for l in log_tail('lab7_02_spi_tx_tb_icarus.txt', 't=')][:4] +
                            ['...  (8 bytes)', '[Icarus·Vivado] PASS: SCK 500 kHz, Mode 0 timing,',
                             '                UART TX= lines match',
                             '$ slave < fpga_tx_bytes.hex   (MCU 수신 VCP)',
                             ' '.join(result_text('slave_from_fpga_vcp.txt').replace('\r', '').split())]),
             size=6.0, link=gh(f'{logs}/lab7_02_spi_tx_tb_icarus.txt'), label='로그')
    fig = add_figure(doc, IMG / 'vivado' / 'lab7_02_spi_tx_tb_view.png',
                     'FPGA 송신 Vivado 파형(tb_view, 송신 간격 40 µs). start 뒤 state가 1→2·3 반복→4→5로 가며 SCK 8주기가 나오고, '
                     'TB가 상승 에지에서 모은 got이 55, a5가 된다.', fig)
    add_text(doc, 'cs_n이 내려가는 순간 mosi가 이미 bit7 값이고(0x55면 0, 0xA5면 1), 첫 SCK 상승 에지는 1 µs 뒤다. mosi는 SCK 하강과 같은 '
                  '시각에만 바뀐다. bit_index가 7이 된 뒤 TRAIL·GAP을 지나 done이 한 클록 나오고, 그때 value가 LED와 UART로 간다.')
    fig = add_figure(doc, IMG / 'vivado' / 'lab7_02_spi_tx_tb.png',
                     'FPGA 송신 Vivado 전체 파형(tb, 약 87 ms). 10 ms마다 value가 55·a5·00·ff로 바뀌며 한 바이트씩 나가고 '
                     'txd로 "TX=" 줄이 뒤따른다.', fig)
    add_heading(doc, '구현 결과와 보드에서 확인할 항목', 2)
    add_table(doc, ['항목', '값'], [
        ['LUT · 레지스터', '116개 · 125개'],
        ['타이밍', '50 MHz에서 WNS +15.484 ns, 위반 없음'],
        ['DRC', '오류 0, 경고 1 (CFGBVS 미설정)'],
        ['핀', 'F8 SCK, E8 MOSI, A7 CS_n (수신 설계와 같음)'],
        ['bitstream', 'lab7_02_spi_tx/bitstream/spi_tx_uart.bit'],
    ], [0.9, 2.32], size=7.2)
    add_link_line(doc, 'XDC', gh(f'{D2}/constraints/spi_tx_uart.xdc'))
    add_text(doc, '매뉴얼대로 MCU에 잇기 전에 오실로스코프로 먼저 본다. 그다음 MCU에 수신 프로그램(-DSTM32_3_ROLE=2)을 올리고 나서 선을 잇는다.')
    add_table(doc, ['확인 항목', '예상 관찰'], [
        ['SCK', '주기 2 µs(500 kHz), 바이트마다 8주기'],
        ['CS_n', '1초마다 17 µs LOW'],
        ['CS↓ → 첫 SCK↑', '1 µs, 이때 MOSI = bit7'],
        ['FPGA COM', '1초마다 TX=55, A5, 00, FF'],
        ['MCU VCP', 'RX=값이 FPGA의 TX=와 같음'],
        ['클록 스위치 F 아님', 'SCK·간격이 같은 비율로 느려짐'],
    ], [0.95, 2.27], size=7.0)

    # ================================================================= 과제12
    add_heading(doc, 'STM32_3 과제12 FPGA → FPGA 송수신 확인', 1)
    add_text(doc, '지정된 두 조가 FPGA를 하나씩 맡아, 한쪽에 과제11의 송신 bitstream, 다른 쪽에 과제10의 수신 bitstream을 올린다. 두 설계의 핀이 '
                  '같으므로 BDIO_0끼리, BDIO_1끼리, BDIO_2끼리, GND끼리 잇는다(그림 2). 수신 FPGA의 UART에 나오는 RX=값이 송신 FPGA의 '
                  'TX=값과 같은지 본다. 역할 교대는 두 보드의 bitstream을 바꿔 올리는 것이며 선은 그대로 둔다.')
    add_text(doc, '두 보드는 각자의 50 MHz 발진기를 쓰므로 클록 주파수와 위상이 조금씩 다르다. 수신 회로가 SCK를 입력으로 받아 자기 클록에 동기화하는 '
                  '구조라 이 차이는 문제가 되지 않아야 한다. 이를 확인하려고 lab7_03_spi_link에 두 설계를 함께 넣은 테스트벤치를 만들었다. '
                  '보드 A 클록은 20.000 ns, 보드 B는 20.050 ns(0.25 % 느림, 위상 7 ns 어긋남)이고, 선 지연으로 SCK 3 ns, MOSI 5 ns, CS 4 ns를 '
                  '더했다. 두 UART 출력을 각각 PC 쪽에서 받아 비교한다.')
    add_code(doc, '\n'.join(log_tail('lab7_03_spi_link_tb_icarus.txt', 't=')[:4] +
                            ['...  (8 bytes)', '[Icarus·Vivado] PASS: board A TX = board B RX',
                             '                (separate clocks, wire delay)']), size=6.0,
             link=gh(f'{logs}/lab7_03_spi_link_tb_icarus.txt'), label='로그')
    fig = add_figure(doc, IMG / 'vivado' / 'lab7_03_spi_link_tb_view.png',
                     'FPGA–FPGA Vivado 파형(tb_view). 보드 A의 sck_a가 선 지연 뒤 sck_b로 보드 B에 들어가고, B 안에서 sck_rise 8번 뒤 '
                     'rx_data와 led_b가 55, a5가 된다.', fig)
    fig = add_figure(doc, IMG / 'vivado' / 'lab7_03_spi_link_tb.png',
                     'FPGA–FPGA Vivado 전체 파형(tb). A가 10 ms마다 보낸 값을 B가 받아 rx_valid 뒤 txd_b로 "RX=" 줄을 내고, txd_a의 "TX=" 줄과 '
                     '값이 같다.', fig)
    add_table(doc, ['확인 항목', '예상 관찰'], [
        ['배선 전', '두 보드 bitstream 확인(송신 1, 수신 1)'],
        ['양쪽 SW5, GND', 'BDIO 연결 켬, GND 공통'],
        ['수신 FPGA COM', 'RX=55, A5, 00, FF 반복'],
        ['송신 FPGA COM', 'TX= 같은 순서(두 PC 화면 비교)'],
        ['역할 교대', 'bitstream만 바꿔 같은 결과'],
    ], [0.95, 2.27], size=7.0)

    # ---- 결론
    add_heading(doc, '4 예상 결과 정리와 실험 계획', 1)
    add_text(doc, '이번 주의 공통점은 같은 바이트를 서로 다른 장치가 같은 규칙으로 읽는 것이다. Mode 0에서는 보내는 쪽이 하강 에지에 비트를 바꾸고 '
                  '받는 쪽이 상승 에지에 읽으므로, SCK 반주기만큼의 여유가 생긴다. MCU는 SPI 하드웨어가 이를 처리하고, FPGA는 같은 규칙을 '
                  '상태 기계(송신)와 동기화·에지 검출(수신)로 직접 만든다. 어느 연결이든 받는 쪽 출력(RX=)이 보낸 쪽 출력(TX=)과 같은지로 '
                  '판단한다.')
    add_table(doc, ['순서', '할 일', '기록할 것'], [
        ['1', '과제8 기본 빌드 다운로드', 'VCP 화면, SCK·MOSI·CS 파형'],
        ['2', '0x55 고정·주기 측정', 'SCK 주기, CS↓→SCK 시간'],
        ['3', '과제9 수신 먼저, 송신 나중', '두 VCP 화면, 배선 사진'],
        ['4', '과제9 역할 교대', 'CS 선 변경, 결과 화면'],
        ['5', 'spi_rx_uart.bit, 과제10', 'FPGA COM 화면, LED'],
        ['6', 'spi_tx_uart.bit, 파형', 'SCK 2 µs, CS 17 µs'],
        ['7', 'MCU 수신 후 연결, 과제11', 'MCU VCP, FPGA COM'],
        ['8', '과제12 두 보드, 교대', '두 COM 화면, 배선 사진'],
    ], [0.42, 1.4, 1.4], size=7.2)
    add_text(doc, '실험 후 보고서에서는 오실로스코프로 잰 SCK 주기·CS 시간과 이 보고서의 계산값(1.28 µs, 2 µs, 17 µs)을 비교하고, MCU HAL이 CS와 '
                  'SCK 사이에 넣는 시간을 적는다. 값이 밀리거나 틀린 경우가 있으면 그때의 연결·실행 순서와 함께 원인을 정리한다.')

    add_heading(doc, '참고 문헌', 1)
    add_text(doc, '[1] STMicroelectronics, STM32CubeG4 MCU Firmware Package (stm32g4xx_hal_spi.c). '
                  'https://github.com/STMicroelectronics/STM32CubeG4', size=9.0)
    add_text(doc, '[2] Sarah L. Harris and David Harris, Digital Design and Computer Architecture: ARM Edition, Morgan Kaufmann, '
                  '2015. ISBN 978-0-12-800056-4.', size=9.0)

    doc.core_properties.title = 'LAB7 예비 보고서'
    doc.core_properties.subject = 'STM32_3 SPI, MCU·FPGA 송수신'
    doc.core_properties.author = '김태이'
    doc.save(OUT)
    print(OUT)


if __name__ == '__main__':
    build()
