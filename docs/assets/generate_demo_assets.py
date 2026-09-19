"""Generate the illustrative, synthetic demo assets used by the README and landing page."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SCALE = 2
BG = "#0b0d12"
PANEL = "#171a21"
PANEL_ALT = "#1f232c"
TEXT = "#f4f4f5"
MUTED = "#a1a1aa"
YELLOW = "#eab308"
RED = "#ef4444"
BLUE = "#3b82f6"
GRAY = "#52525b"
BORDER = "#2b303b"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    font_path = Path("C:/Windows/Fonts") / name
    if not font_path.is_file():
        raise FileNotFoundError(font_path)
    return ImageFont.truetype(str(font_path), size * SCALE)


FONT_EN = lambda size: font("segoeui.ttf", size)
FONT_EN_BOLD = lambda size: font("segoeuib.ttf", size)
FONT_ZH = lambda size: font("msyh.ttc", size)
FONT_ZH_BOLD = lambda size: font("msyhbd.ttc", size)


def canvas(width: int, height: int) -> Image.Image:
    return Image.new("RGB", (width * SCALE, height * SCALE), BG)


def scaled_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(value * SCALE for value in box)


def draw_panel(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    rows: list[tuple[str, str, str]],
    label: str,
    title_font: ImageFont.FreeTypeFont,
    row_font: ImageFont.FreeTypeFont,
    sub_font: ImageFont.FreeTypeFont,
    label_font: ImageFont.FreeTypeFont,
) -> None:
    draw.rounded_rectangle(scaled_box(box), radius=18 * SCALE, fill=PANEL, outline=BORDER, width=SCALE)
    left, top, right, _ = box
    draw.text((left * SCALE + 22 * SCALE, top * SCALE + 18 * SCALE), title, font=title_font, fill=TEXT)
    draw.text(
        (left * SCALE + 22 * SCALE, top * SCALE + 50 * SCALE),
        label,
        font=label_font,
        fill=MUTED,
    )
    row_top = top + 84
    for index, (name, detail, color) in enumerate(rows):
        y = row_top + index * 56
        draw.rounded_rectangle(
            scaled_box((left + 16, y, right - 16, y + 46)),
            radius=12 * SCALE,
            fill=PANEL_ALT,
        )
        draw.ellipse(
            scaled_box((left + 32, y + 16, left + 46, y + 30)),
            fill=color,
        )
        draw.text(
            ((left + 58) * SCALE, (y + 9) * SCALE),
            name,
            font=row_font,
            fill=TEXT,
        )
        draw.text(
            ((left + 58) * SCALE, (y + 28) * SCALE),
            detail,
            font=sub_font,
            fill=MUTED,
        )


def render_before(language: str) -> Image.Image:
    image = canvas(960, 540)
    draw = ImageDraw.Draw(image)
    if language == "zh":
        title_font, row_font, sub_font, label_font = FONT_ZH_BOLD(19), FONT_ZH(17), FONT_ZH(12), FONT_ZH(12)
        rows = [
            ("整理文档", "更新于 10:05", GRAY),
            ("完善接口", "更新于 09:55", GRAY),
            ("修复测试", "更新于 10:01", GRAY),
        ]
        panel_title = "按最近更新时间"
        panel_label = "所有状态看起来差不多"
        heading = "Before：只看更新时间"
        note = "合成任务演示；不是真实账号数据。"
    else:
        title_font, row_font, sub_font, label_font = FONT_EN_BOLD(19), FONT_EN(17), FONT_EN(12), FONT_EN(12)
        rows = [
            ("Edit docs", "updated 10:05", GRAY),
            ("Update API", "updated 09:55", GRAY),
            ("Fix tests", "updated 10:01", GRAY),
        ]
        panel_title = "Ordered by latest update"
        panel_label = "Every state looks about the same"
        heading = "Before: update-time order"
        note = "Illustrative synthetic tasks; no real account data."
    draw.text((60 * SCALE, 42 * SCALE), heading, font=FONT_EN_BOLD(30) if language == "en" else FONT_ZH_BOLD(30), fill=TEXT)
    draw.text((60 * SCALE, 88 * SCALE), note, font=label_font, fill=MUTED)
    draw_panel(image, draw, (60, 132, 900, 486), panel_title, rows, panel_label, title_font, row_font, sub_font, label_font)
    return image.resize((960, 540), Image.Resampling.LANCZOS)


def render_after(language: str) -> Image.Image:
    image = canvas(960, 540)
    draw = ImageDraw.Draw(image)
    if language == "zh":
        title_font, row_font, sub_font, label_font = FONT_ZH_BOLD(19), FONT_ZH(17), FONT_ZH(12), FONT_ZH(12)
        rows = [
            ("修复测试", "黄色：等待实施计划", YELLOW),
            ("完善接口", "红色：置顶关注", RED),
            ("整理文档", "蓝色：普通未读", BLUE),
        ]
        panel_title = "按实际开始时间"
        panel_label = "颜色告诉你下一步看哪个"
        heading = "After：开始时间排序 + 状态颜色"
        note = "合成任务演示；不是真实账号数据。"
    else:
        title_font, row_font, sub_font, label_font = FONT_EN_BOLD(19), FONT_EN(17), FONT_EN(12), FONT_EN(12)
        rows = [
            ("Fix tests", "yellow: plan waiting", YELLOW),
            ("Update API", "red: pinned attention", RED),
            ("Edit docs", "blue: ordinary unread", BLUE),
        ]
        panel_title = "Ordered by actual start"
        panel_label = "Colors show what needs attention next"
        heading = "After: start-time order + attention colors"
        note = "Illustrative synthetic tasks; no real account data."
    draw.text((60 * SCALE, 42 * SCALE), heading, font=FONT_EN_BOLD(30) if language == "en" else FONT_ZH_BOLD(30), fill=TEXT)
    draw.text((60 * SCALE, 88 * SCALE), note, font=label_font, fill=MUTED)
    draw_panel(image, draw, (60, 132, 900, 486), panel_title, rows, panel_label, title_font, row_font, sub_font, label_font)
    return image.resize((960, 540), Image.Resampling.LANCZOS)


def render_feature(language: str, focus: str) -> Image.Image:
    image = render_after(language).copy()
    draw = ImageDraw.Draw(image)
    if focus == "yellow":
        box = (44, 204, 916, 274)
        text = "黄色 = 等待确认计划" if language == "zh" else "Yellow = plan waiting"
    elif focus == "red":
        box = (44, 260, 916, 330)
        text = "红色 = 置顶关注" if language == "zh" else "Red = pinned attention"
    else:
        box = (44, 316, 916, 386)
        text = "蓝色 = 普通未读" if language == "zh" else "Blue = ordinary unread"
    draw.rounded_rectangle(scaled_box(box), radius=14 * SCALE, outline="#ffffff", width=2 * SCALE)
    draw.rounded_rectangle(
        scaled_box((620, 80, 900, 122)),
        radius=12 * SCALE,
        fill=PANEL_ALT,
    )
    draw.text(
        (642 * SCALE, 92 * SCALE),
        text,
        font=FONT_ZH_BOLD(17) if language == "zh" else FONT_EN_BOLD(17),
        fill=TEXT,
    )
    return image


def build_before_after(language: str) -> Image.Image:
    width, height = 1280, 720
    image = canvas(width, height)
    draw = ImageDraw.Draw(image)
    if language == "zh":
        heading = "同样的三个任务，换一种读法"
        left_label, right_label = "按更新时间", "按实际开始时间"
        note = "合成任务演示；不是真实账号数据，也不属于 OpenAI。"
        title_font, label_font = FONT_ZH_BOLD(30), FONT_ZH(15)
    else:
        heading = "The same three tasks, read in a different order"
        left_label, right_label = "By latest update", "By actual start"
        note = "Illustrative synthetic tasks; not affiliated with OpenAI."
        title_font, label_font = FONT_EN_BOLD(30), FONT_EN(15)
    draw.text((60 * SCALE, 44 * SCALE), heading, font=title_font, fill=TEXT)
    draw.text((60 * SCALE, 90 * SCALE), note, font=label_font, fill=MUTED)
    for index, side in enumerate((("left", left_label), ("right", right_label))):
        offset = 60 + index * 610
        draw.text((offset * SCALE, 138 * SCALE), side[1], font=FONT_EN_BOLD(19) if language == "en" else FONT_ZH_BOLD(19), fill=TEXT)
        rows = (
            [("整理文档", "10:05", GRAY), ("完善接口", "09:55", GRAY), ("修复测试", "10:01", GRAY)]
            if language == "zh" and index == 0
            else [("修复测试", "10:00", YELLOW), ("完善接口", "09:50", RED), ("整理文档", "09:10", BLUE)]
            if language == "zh"
            else [("Edit docs", "10:05", GRAY), ("Update API", "09:55", GRAY), ("Fix tests", "10:01", GRAY)]
            if index == 0
            else [("Fix tests", "10:00", YELLOW), ("Update API", "09:50", RED), ("Edit docs", "09:10", BLUE)]
        )
        draw.rounded_rectangle(scaled_box((offset, 174, offset + 560, 626)), radius=18 * SCALE, fill=PANEL, outline=BORDER, width=SCALE)
        for row_index, (name, detail, color) in enumerate(rows):
            y = 204 + row_index * 96
            draw.rounded_rectangle(scaled_box((offset + 20, y, offset + 540, y + 76)), radius=12 * SCALE, fill=PANEL_ALT)
            draw.ellipse(scaled_box((offset + 42, y + 28, offset + 62, y + 48)), fill=color)
            draw.text(((offset + 82) * SCALE, (y + 16) * SCALE), name, font=FONT_EN_BOLD(20) if language == "en" else FONT_ZH_BOLD(20), fill=TEXT)
            draw.text(((offset + 82) * SCALE, (y + 46) * SCALE), detail, font=FONT_EN(14) if language == "en" else FONT_ZH(14), fill=MUTED)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def build_social_preview() -> Image.Image:
    width, height = 1280, 640
    image = canvas(width, height)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(scaled_box((60, 60, 1220, 580)), radius=28 * SCALE, fill=PANEL, outline=BORDER, width=SCALE)
    draw.text((110 * SCALE, 116 * SCALE), "codex-desktop-workflow", font=FONT_EN_BOLD(48), fill=TEXT)
    draw.text(
        (112 * SCALE, 182 * SCALE),
        "Priority-aware sorting and attention colors",
        font=FONT_EN(25),
        fill=MUTED,
    )
    draw.text(
        (112 * SCALE, 222 * SCALE),
        "for Codex Desktop, built as a verified local copy.",
        font=FONT_EN(25),
        fill=MUTED,
    )
    for index, (color, label) in enumerate(
        ((YELLOW, "plan waiting"), (RED, "pinned"), (BLUE, "unread"))
    ):
        x = 112 + index * 330
        draw.ellipse(scaled_box((x, 342, x + 28, 370)), fill=color)
        draw.text(
            ((x + 44) * SCALE, 342 * SCALE),
            label,
            font=FONT_EN_BOLD(21),
            fill=TEXT,
        )
    draw.text(
        (112 * SCALE, 470 * SCALE),
        "github.com/catterhu1207-ux/codex-desktop-workflow",
        font=FONT_EN(20),
        fill=MUTED,
    )
    draw.text(
        (112 * SCALE, 510 * SCALE),
        "Unofficial project. Not affiliated with OpenAI.",
        font=FONT_EN(16),
        fill=MUTED,
    )
    return image.resize((width, height), Image.Resampling.LANCZOS)


def main() -> None:
    for language in ("en", "zh"):
        before = render_before(language)
        after = render_after(language)
        frames = [
            before,
            after,
            render_feature(language, "yellow"),
            render_feature(language, "red"),
            render_feature(language, "blue"),
        ]
        frames[0].save(
            ROOT / f"demo-{language}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=1400,
            loop=0,
            optimize=True,
            disposal=2,
        )
        build_before_after(language).save(ROOT / f"before-after-{language}.png", optimize=True)
    build_social_preview().save(ROOT / "social-preview.png", optimize=True)


if __name__ == "__main__":
    main()
